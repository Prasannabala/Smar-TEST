import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class VisibleBlock extends Block {
  readonly name = 'AssertVisible';
  readonly requiredParams = ['selector'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await expect(page.locator(data['selector'] as string)).toBeVisible();
  }
}

BlockRegistry.register('AssertVisible', VisibleBlock);
