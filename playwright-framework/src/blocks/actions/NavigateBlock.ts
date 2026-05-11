import { Page } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class NavigateBlock extends Block {
  readonly name = 'Navigate';
  readonly requiredParams = ['url'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    await page.goto(data['url'] as string);
  }
}

BlockRegistry.register('Navigate', NavigateBlock);
