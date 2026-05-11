import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class UrlAssertBlock extends Block {
  readonly name = 'AssertUrl';
  readonly requiredParams = ['url'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await expect(page).toHaveURL(data['url'] as string);
  }
}

BlockRegistry.register('AssertUrl', UrlAssertBlock);
