import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class SelectBlock extends Block {
  readonly name = 'Select';
  readonly requiredParams = ['selector', 'value'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await page.locator(data['selector'] as string).selectOption(data['value'] as string);
  }
}

BlockRegistry.register('Select', SelectBlock);
