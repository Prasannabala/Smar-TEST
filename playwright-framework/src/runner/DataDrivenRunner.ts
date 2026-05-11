import { Page } from '@playwright/test';
import { BlockData } from '../blocks/base/Block';
import { BlockRegistry } from '../blocks/base/BlockRegistry';
import { logger } from '../utils/logger';

export interface ScenarioStep {
  block: string;
  data: BlockData;
}

export interface Scenario {
  name: string;
  steps: ScenarioStep[];
}

export interface TestDataFile {
  scenarios: Scenario[];
}

/**
 * Executes an ordered list of LEGO block steps for a single test scenario.
 * Each step specifies its block by name and provides its own data slice —
 * multiple Fill blocks in one scenario each carry their own selector/value.
 *
 * Usage in a generated spec file:
 *   const runner = new DataDrivenRunner();
 *   for (const scenario of testData.scenarios) {
 *     test(scenario.name, async ({ page }) => {
 *       await runner.run(page, scenario.steps);
 *     });
 *   }
 */
export class DataDrivenRunner {
  async run(page: Page, steps: ScenarioStep[]): Promise<void> {
    for (const step of steps) {
      const block = BlockRegistry.get(step.block);
      logger.info(`  → ${step.block}`);
      await block.execute(page, step.data);
    }
  }
}
