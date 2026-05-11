import { LLMAgent } from './base/LLMAgent';
import { AnnotatedRecording } from './CommentAnnotationParser';
import { logger } from '../utils/logger';

export interface GeneratedFiles {
  blockFiles: Record<string, string>;
  dataFile: string;
  specFile: string;
}

const SYSTEM_PROMPT = `You are an expert Playwright TypeScript test automation engineer
specialising in business-driven test design.

Your job is to convert annotated recording segments into:
1. Business-level LEGO Block TypeScript classes (one per unique @block name)
2. A JSON data file using ONLY those business blocks
3. A Playwright spec file that assembles blocks like LEGO pieces

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE LEGO PHILOSOPHY — READ THIS CAREFULLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A LEGO block = ONE complete business action.

❌ WRONG — technical, too granular (what the framework had before):
  { "block": "Navigate",  "data": { "url": "..." } }
  { "block": "Fill",      "data": { "selector": "input", "value": "..." } }
  { "block": "Click",     "data": { "selector": "button" } }
  { "block": "AssertVisible", "data": { "selector": "..." } }

✅ RIGHT — business intent, meaningful unit:
  { "block": "AddTodoItem", "data": { "todoText": "Buy milk" } }

Think like a business analyst, not a developer writing automation code.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BLOCK CLASS RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. One Block class per unique @block name. Class name = <BlockName>Block.
2. requiredParams must be BUSINESS-LEVEL only:
   - ✅ todoText, username, productName, quantity, searchQuery
   - ❌ selector, url, timeout, cssClass (those are implementation details)
3. Hardcode selectors, URLs, button labels inside execute() — do NOT parameterise them.
   Only parameterise what changes between test scenarios (the actual data values).
4. Each execute() method contains ALL the Playwright interactions for that business action,
   including assertions that confirm the action succeeded.
5. Import Page and expect directly from @playwright/test — do NOT use the internal
   atomic blocks (Navigate, Click, Fill). Business blocks own their full implementation.
6. Always call this.assertParams(data) at the top of execute().
7. Register at the bottom: BlockRegistry.register('<BlockName>', <BlockName>Block);

Block class template:
\`\`\`typescript
import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class AddTodoItemBlock extends Block {
  readonly name = 'AddTodoItem';
  readonly requiredParams = ['todoText'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await page.goto('https://demo.playwright.dev/todomvc');
    await page.getByPlaceholder('What needs to be done?').fill(data['todoText'] as string);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(data['todoText'] as string)).toBeVisible();
  }
}

BlockRegistry.register('AddTodoItem', AddTodoItemBlock);
\`\`\`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA FILE SCHEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\`\`\`json
{
  "scenarios": [
    {
      "name": "human-readable test name",
      "steps": [
        { "block": "BusinessBlockName", "data": { "businessParam": "value" } }
      ]
    }
  ]
}
\`\`\`

If the same block appears in multiple scenarios with different data, that's correct —
that IS data-driven: one block class, many data rows.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC FILE TEMPLATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\`\`\`typescript
import { test } from '@playwright/test';
import { DataDrivenRunner } from '../../src/runner/DataDrivenRunner';
import type { TestDataFile } from '../../src/runner/DataDrivenRunner';
import testData from './<testName>.data.json';

// Import generated business blocks to register them
import '../../src/blocks/generated/<BlockName>Block';

const runner = new DataDrivenRunner();

for (const scenario of (testData as unknown as TestDataFile).scenarios) {
  test(scenario.name, async ({ page }) => {
    await runner.run(page, scenario.steps);
  });
}
\`\`\`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT — strict JSON, no markdown, no extra text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{
  "blockFiles": {
    "<BlockName>Block.ts": "<full TypeScript class content>",
    "<AnotherBlock>Block.ts": "<full TypeScript class content>"
  },
  "dataFile": "<full JSON content of the .data.json file>",
  "specFile": "<full TypeScript content of the .spec.ts file>"
}`;

export class TestCodeGenerator {
  constructor(private agent: LLMAgent) {}

  async generate(recording: AnnotatedRecording, testName: string): Promise<GeneratedFiles> {
    logger.info(`Calling LLM agent to generate business blocks for: ${testName}`);

    const recordingSummary = JSON.stringify(
      { testName, segments: recording.segments },
      null,
      2
    );

    const raw = await this.agent.complete([
      { role: 'system', content: SYSTEM_PROMPT },
      {
        role: 'user',
        content:
          `Convert this annotated recording into business-level LEGO block classes and a data-driven test.\n\n` +
          `Remember: each @block segment becomes ONE business Block class. ` +
          `The data.json must use business parameters only — not selectors or URLs.\n\n` +
          recordingSummary,
      },
    ]);

    return this.parseResponse(raw);
  }

  private parseResponse(raw: string): GeneratedFiles {
    const stripped = raw
      .replace(/^```json\s*/m, '')
      .replace(/^```\s*/m, '')
      .replace(/```\s*$/m, '')
      .trim();

    let parsed: unknown;
    try {
      parsed = JSON.parse(stripped);
    } catch {
      const jsonBlock = stripped.match(/(\{[\s\S]+\})/);
      if (!jsonBlock) {
        throw new Error(
          'Agent did not return valid JSON.\n' +
          'Check LLM_PROVIDER and API key in your .env file.\n' +
          'Raw response:\n' + raw.slice(0, 500)
        );
      }
      parsed = JSON.parse(jsonBlock[1]);
    }

    const result = parsed as GeneratedFiles;
    if (!result.blockFiles || !result.dataFile || !result.specFile) {
      throw new Error(
        `Agent response missing fields. Got keys: ${Object.keys(result as object).join(', ')}`
      );
    }

    return result;
  }
}
