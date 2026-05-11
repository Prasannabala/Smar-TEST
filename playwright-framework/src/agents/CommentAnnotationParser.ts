import * as fs from 'fs';
import * as path from 'path';

export interface DataEntry {
  key: string;
  value: string;
}

export interface ScenarioSegment {
  blockName: string;
  scenarioName: string;
  steps: string[];
  data: DataEntry[];
  params: string[];
}

export interface AnnotatedRecording {
  filePath: string;
  segments: ScenarioSegment[];
}

const RE_SCENARIO = /\/\/\s*@scenario:\s*(.+)/;
const RE_BLOCK_START = /\/\/\s*@block:\s*(\w+)/;
const RE_BLOCK_END = /\/\/\s*@end-block/;
const RE_DATA_LINE = /\/\/\s*@data:\s*(\w+)\s*=\s*["']?([^"'\n]+?)["']?\s*$/;
const RE_PARAM_INLINE = /@param:\s*(\w+)/;
const RE_DATA_INLINE = /@data:\s*(\w+)\s*=\s*["']?([^"'\n]+?)["']?\s*$/;

/**
 * Parses a Playwright recording file annotated with @block / @data / @param / @scenario tags.
 * Pure TypeScript — no LLM required.
 *
 * Tag reference:
 *   // @scenario: My Test         — names the next test scenario
 *   // @block: BlockName          — opens a named LEGO block segment
 *   // @end-block                 — closes the current segment
 *   // @data: key = "value"       — standalone data declaration above a code line
 *   await page.goto('url');  // @param: paramName   — marks inline value as a parameter
 *   await page.fill('x', 'v');   // @data: key = "v" — inline data tag
 */
export class CommentAnnotationParser {
  parse(filePath: string): AnnotatedRecording {
    const resolved = path.resolve(filePath);
    const content = fs.readFileSync(resolved, 'utf-8');
    return this.parseContent(content, resolved);
  }

  parseContent(content: string, filePath = '<inline>'): AnnotatedRecording {
    const lines = content.split('\n');
    const segments: ScenarioSegment[] = [];

    let currentScenario = 'Default Scenario';
    let currentSegment: ScenarioSegment | null = null;
    let pendingData: DataEntry[] = [];

    for (const rawLine of lines) {
      const line = rawLine.trim();

      const scenarioMatch = line.match(RE_SCENARIO);
      if (scenarioMatch) {
        currentScenario = scenarioMatch[1].trim();
        continue;
      }

      const blockStartMatch = line.match(RE_BLOCK_START);
      if (blockStartMatch) {
        currentSegment = {
          blockName: blockStartMatch[1].trim(),
          scenarioName: currentScenario,
          steps: [],
          data: [],
          params: [],
        };
        pendingData = [];
        continue;
      }

      if (RE_BLOCK_END.test(line)) {
        if (currentSegment) {
          segments.push(currentSegment);
        }
        currentSegment = null;
        pendingData = [];
        continue;
      }

      // Standalone @data comment line (applies to the next code line)
      const standaloneData = line.match(RE_DATA_LINE);
      if (standaloneData) {
        pendingData.push({ key: standaloneData[1], value: standaloneData[2].trim() });
        continue;
      }

      // Code line (not a pure comment line)
      if (currentSegment && line && !line.startsWith('//')) {
        currentSegment.steps.push(line);

        // Flush any pending @data declarations onto this step
        if (pendingData.length > 0) {
          currentSegment.data.push(...pendingData);
          pendingData = [];
        }

        // Inline @param tag on the same line
        const paramMatch = line.match(RE_PARAM_INLINE);
        if (paramMatch) {
          currentSegment.params.push(paramMatch[1]);
        }

        // Inline @data tag on the same line
        const inlineData = line.match(RE_DATA_INLINE);
        if (inlineData) {
          currentSegment.data.push({ key: inlineData[1], value: inlineData[2].trim() });
        }
      }
    }

    // Close any block that wasn't explicitly ended
    if (currentSegment) {
      segments.push(currentSegment);
    }

    return { filePath, segments };
  }
}
