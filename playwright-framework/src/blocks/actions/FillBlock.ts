import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class FillBlock extends Block {
  readonly name = 'Fill';
  readonly requiredParams = ['selector', 'value'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await page.locator(data['selector'] as string).fill(data['value'] as string);
  }
}

BlockRegistry.register('Fill', FillBlock);
