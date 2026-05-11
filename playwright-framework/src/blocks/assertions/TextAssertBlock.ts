import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class TextAssertBlock extends Block {
  readonly name = 'AssertText';
  readonly requiredParams = ['selector', 'text'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await expect(page.locator(data['selector'] as string)).toContainText(data['text'] as string);
  }
}

BlockRegistry.register('AssertText', TextAssertBlock);
