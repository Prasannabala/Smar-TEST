import { test, expect } from '@playwright/test';

/**
 * RAW PLAYWRIGHT CODEGEN RECORDING — ANNOTATED FOR LEGO CONVERSION
 * ─────────────────────────────────────────────────────────────────
 * This file is the INPUT to the converter.  Do NOT run it directly.
 *
 * Workflow:
 *   1. Record with:   npm run record https://demo.playwright.dev/todomvc
 *   2. Annotate with  @scenario / @block / @data / @param / @end-block tags
 *   3. Convert with:  npm run convert recordings/example-todo.recording.ts
 *
 * Output:
 *   tests/generated/example-todo.spec.ts     ← data-driven Playwright test
 *   tests/generated/example-todo.data.json   ← extracted test data
 * ─────────────────────────────────────────────────────────────────
 */

test('recorded test', async ({ page }) => {

  // ── Scenario 1 ────────────────────────────────────────────────
  // @scenario: Add a single todo item
  // @block: AddTodoItem
  await page.goto('https://demo.playwright.dev/todomvc'); // @param: baseUrl
  // @step: Type a new todo
  // @data: todoText = "Buy groceries"
  await page.getByPlaceholder('What needs to be done?').fill('Buy groceries');
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  // @step: Verify item appears in the list
  await expect(page.getByText('Buy groceries')).toBeVisible(); // @param: assertText
  // @end-block

  // ── Scenario 2 ────────────────────────────────────────────────
  // @scenario: Add multiple todo items
  // @block: AddTodoItem
  await page.goto('https://demo.playwright.dev/todomvc'); // @param: baseUrl
  // @data: todoText = "Read a book"
  await page.getByPlaceholder('What needs to be done?').fill('Read a book');
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  await expect(page.getByText('Read a book')).toBeVisible(); // @param: assertText
  // @end-block

  // ── Scenario 3 ────────────────────────────────────────────────
  // @scenario: Complete a todo item
  // @block: CompleteTodo
  await page.goto('https://demo.playwright.dev/todomvc'); // @param: baseUrl
  // @data: todoText = "Walk the dog"
  await page.getByPlaceholder('What needs to be done?').fill('Walk the dog');
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  // @step: Click the complete checkbox
  await page.getByRole('checkbox', { name: 'Walk the dog' }).check();
  // @step: Switch to Completed filter
  await page.getByRole('link', { name: 'Completed' }).click();
  await expect(page.getByText('Walk the dog')).toBeVisible(); // @param: assertText
  // @end-block

});
