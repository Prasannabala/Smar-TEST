import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class WaitBlock extends Block {
  readonly name = 'Wait';
  readonly requiredParams = [];

  async execute(page: Page, data: BlockData): Promise<void> {
    if (data['timeout']) {
      await page.waitForTimeout(data['timeout'] as number);
    } else if (data['selector']) {
      await page.locator(data['selector'] as string).waitFor({ state: 'visible' });
    } else {
      throw new Error("WaitBlock requires either 'selector' or 'timeout' in data.");
    }
  }
}

BlockRegistry.register('Wait', WaitBlock);
