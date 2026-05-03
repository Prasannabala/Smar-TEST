import { LLMAgent } from './base/LLMAgent';
import { AnnotatedRecording } from './CommentAnnotationParser';
import { logger } from '../utils/logger';

export interface GeneratedFiles {
  dataFile: string;
  specFile: string;
}

const SYSTEM_PROMPT = `You are an expert Playwright TypeScript test automation engineer.

Your job is to convert annotated recording data into two files:
1. A JSON data file (<testName>.data.json) following the scenario-step schema
2. A Playwright spec file (<testName>.spec.ts) using the LEGO block framework

## LEGO Block Framework

Available blocks and their required data keys:
| Block          | Required data keys                                                      |
|----------------|-------------------------------------------------------------------------|
| Navigate       | url                                                                     |
| Click          | selector                                                                |
| Fill           | selector, value                                                         |
| Select         | selector, value                                                         |
| Wait           | selector OR timeout (ms)                                                |
| AssertUrl      | url                                                                     |
| AssertText     | selector, text                                                          |
| AssertVisible  | selector                                                                |
| Login          | baseUrl, emailSelector, email, passwordSelector, password, submitSelector, expectedUrl |

## Data File Schema (strict)
\`\`\`json
{
  "scenarios": [
    {
      "name": "human-readable scenario name",
      "steps": [
        { "block": "BlockName", "data": { "key": "value" } }
      ]
    }
  ]
}
\`\`\`

## Spec File Template
\`\`\`typescript
import { test } from '@playwright/test';
import { DataDrivenRunner } from '../../src/runner/DataDrivenRunner';
import type { TestDataFile } from '../../src/runner/DataDrivenRunner';
import testData from './<testName>.data.json';

// Auto-register all LEGO blocks used in this test
import '../../src/blocks/actions/NavigateBlock';
import '../../src/blocks/actions/FillBlock';
import '../../src/blocks/actions/ClickBlock';
// ... add other imports as needed

const runner = new DataDrivenRunner();

for (const scenario of (testData as TestDataFile).scenarios) {
  test(scenario.name, async ({ page }) => {
    await runner.run(page, scenario.steps);
  });
}
\`\`\`

## Rules
- Each scenario maps to one test() call
- Each step maps to one block execution with its specific data
- Extract seed data values from the @data annotations in the recording
- Keep selectors from the original Playwright code (getByLabel, getByRole, locator, etc.)
- Selector strings must be valid CSS or Playwright locator syntax
- Use composite Login block when you detect a full login flow
- The spec file must import ONLY the block files for blocks actually used

Respond with ONLY valid JSON (no markdown, no commentary):
{
  "dataFile": "<full contents of the .data.json file as a JSON string>",
  "specFile": "<full contents of the .spec.ts file as a string>"
}`;

export class TestCodeGenerator {
  constructor(private agent: LLMAgent) {}

  async generate(recording: AnnotatedRecording, testName: string): Promise<GeneratedFiles> {
    logger.info(`Calling LLM agent to generate test: ${testName}`);

    const recordingSummary = JSON.stringify(
      { testName, segments: recording.segments },
      null,
      2
    );

    const raw = await this.agent.complete([
      { role: 'system', content: SYSTEM_PROMPT },
      {
        role: 'user',
        content: `Convert this annotated recording into a LEGO-block data-driven Playwright test.\n\n${recordingSummary}`,
      },
    ]);

    return this.parseResponse(raw);
  }

  private parseResponse(raw: string): GeneratedFiles {
    // Strip optional markdown code fence
    const stripped = raw
      .replace(/^```json\s*/m, '')
      .replace(/^```\s*/m, '')
      .replace(/```\s*$/m, '')
      .trim();

    let parsed: unknown;
    try {
      parsed = JSON.parse(stripped);
    } catch {
      // Try to extract the first {...} block
      const jsonBlock = stripped.match(/(\{[\s\S]+\})/);
      if (!jsonBlock) {
        throw new Error(
          'Agent did not return valid JSON.\n' +
          'Make sure your LLM_PROVIDER and API key are configured correctly.\n' +
          'Raw response:\n' + raw.slice(0, 500)
        );
      }
      parsed = JSON.parse(jsonBlock[1]);
    }

    const result = parsed as GeneratedFiles;
    if (!result.dataFile || !result.specFile) {
      throw new Error(
        `Agent response is missing 'dataFile' or 'specFile'.\nGot keys: ${Object.keys(result as object).join(', ')}`
      );
    }

    return result;
  }
}
