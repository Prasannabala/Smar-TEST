/**
 * AUTO-GENERATED business block.
 * Source: recordings/example-todo.recording.ts  (@block: CompleteTodo)
 * Regenerate: npm run convert recordings/example-todo.recording.ts
 *
 * Business action: Mark an existing todo item as complete and verify it
 * appears under the Completed filter.
 *
 * Precondition: the todo item must already exist in the list
 * (compose with AddTodoItem in the scenario steps).
 */
import { Page, expect } from '@playwright/test';
import { Block, BlockData } from '../base/Block';
import { BlockRegistry } from '../base/BlockRegistry';

export class CompleteTodoItemBlock extends Block {
  readonly name = 'CompleteTodoItem';
  readonly requiredParams = ['todoText'];

  async execute(page: Page, data: BlockData): Promise<void> {
    this.assertParams(data);
    const todoText = data['todoText'] as string;

    await page.getByRole('checkbox', { name: todoText }).check();
    await page.getByRole('link', { name: 'Completed' }).click();
    await expect(page.getByText(todoText)).toBeVisible();
  }
}

BlockRegistry.register('CompleteTodoItem', CompleteTodoItemBlock);
