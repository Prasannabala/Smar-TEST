/**
 * AUTO-GENERATED business block.
 * Source: recordings/example-todo.recording.ts  (@block: AddTodoItem)
 * Regenerate: npm run convert recordings/example-todo.recording.ts
 *
 * Business action: Add a new item to the TodoMVC list and confirm it appears.
 */
import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class AddTodoItemBlock extends Block {
  readonly name = 'AddTodoItem';
  readonly requiredParams = ['todoText'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    const todoText = data['todoText'] as string;

    await page.goto('https://demo.playwright.dev/todomvc');
    await page.getByPlaceholder('What needs to be done?').fill(todoText);
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText(todoText)).toBeVisible();
  }
}

BlockRegistry.register('AddTodoItem', AddTodoItemBlock);
