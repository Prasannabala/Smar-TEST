import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class ClickBlock extends Block {
  readonly name = 'Click';
  readonly requiredParams = ['selector'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await page.locator(data['selector'] as string).click();
  }
}

BlockRegistry.register('Click', ClickBlock);
