# Agents — Role Reference & Provider Guide

---

## The LEGO Philosophy

**A LEGO block = ONE complete business action.**

Think like a business analyst, not a developer writing automation steps.

```
❌  Too granular (technical interactions — what we avoid):

    scenario: "Add todo item"
    steps:
      - block: Navigate,      data: { url: "https://..." }
      - block: Fill,          data: { selector: "input", value: "Buy milk" }
      - block: Click,         data: { selector: "input" }     ← press Enter
      - block: AssertVisible, data: { selector: "text=Buy milk" }


✅  Business-level (what the framework produces):

    scenario: "Add todo item"
    steps:
      - block: AddTodoItem,   data: { todoText: "Buy milk" }
```

The LEGO block class owns ALL the Playwright interactions internally.
Test authors only see business parameters.

### Composing blocks into scenarios

```
scenario: "Complete a todo item"
steps:
  - block: AddTodoItem,       data: { todoText: "Walk the dog" }
  - block: CompleteTodoItem,  data: { todoText: "Walk the dog" }

scenario: "Full checkout flow"
steps:
  - block: Login,             data: { username: "alice", password: "secret" }
  - block: SearchProduct,     data: { query: "bluetooth headphones" }
  - block: AddToCart,         data: { productName: "Sony WH-1000XM5" }
  - block: Checkout,          data: { address: "123 Main St", card: "4111..." }
  - block: AssertOrderPlaced, data: { expectedConfirmation: "Order #" }
```

Adding more test rows (true data-driven) requires only editing the JSON:

```json
{ "block": "AddTodoItem", "data": { "todoText": "Buy milk"   } },
{ "block": "AddTodoItem", "data": { "todoText": "Read book"  } },
{ "block": "AddTodoItem", "data": { "todoText": "Walk dog"   } }
```

The spec file stays unchanged.

---

## Conversion Pipeline

```
recordings/my-test.recording.ts   ← annotated Playwright codegen output
         │
         ▼
CommentAnnotationParser            ── no LLM, instant ──►  AnnotatedRecording
         │
         ▼
TestCodeGenerator (LLM call)       ────────────────────────────────────────►
         │                                                                  │
         ▼                                                                  │
src/blocks/generated/              ← one .ts file per unique @block name   │
  AddTodoItemBlock.ts                                                       │
  CompleteTodoItemBlock.ts                                                  │
         │                                                                  │
         ▼                                                                  │
tests/generated/                   ← data-driven test output               │
  my-test.data.json                                                         │
  my-test.spec.ts                                                           ◄
```

---

## Agent Roles

### 1. CommentAnnotationParser
**File:** `src/agents/CommentAnnotationParser.ts` | **Type:** Pure TypeScript (no LLM)

Reads the annotated recording and extracts segments from `// @` tags.
Runs first — zero cost, no network.

**Output:** `AnnotatedRecording` — array of `ScenarioSegment` objects with
block name, scenario name, code steps, and extracted data entries.

---

### 2. TestCodeGenerator
**File:** `src/agents/TestCodeGenerator.ts` | **Type:** LLM-powered

Receives the `AnnotatedRecording` and instructs the LLM to:
- Generate a **TypeScript Block class** for each unique `@block` name
- Group all Playwright interactions for that block into `execute(page, data)`
- Identify only the **business-level parameters** (what changes between scenarios)
- Hardcode selectors and URLs inside the class
- Generate `<testName>.data.json` with business-level params
- Generate `<testName>.spec.ts` importing the generated blocks

Prompt caching is enabled on the Anthropic provider to reduce cost on repeated runs.

---

### 3. RecordingConverter
**File:** `src/agents/RecordingConverter.ts` | **Type:** Orchestrator

Ties the pipeline together. Saves:
- Block class files → `src/blocks/generated/<BlockName>Block.ts`
- Data file → `tests/generated/<testName>.data.json`
- Spec file → `tests/generated/<testName>.spec.ts`

---

## Comment Annotation Tag Reference

Add these tags to your Playwright codegen recording before converting.

| Tag | Placement | Effect |
|-----|-----------|--------|
| `// @scenario: Name` | standalone line | Names the next test (`test()` title) |
| `// @block: BusinessName` | standalone line | Opens a named business block segment |
| `// @end-block` | standalone line | Closes the current segment |
| `// @data: key = "value"` | standalone line above a code line | Seeds a data parameter |
| `await ...;  // @param: key` | inline on a code line | Marks the inline value as a parameter |
| `// @step: Description` | standalone line | Labels a step for readability |

### Annotated recording example

```typescript
// @scenario: Add a todo item
// @block: AddTodoItem
await page.goto('https://demo.playwright.dev/todomvc');
// @data: todoText = "Buy groceries"
await page.getByPlaceholder('What needs to be done?').fill('Buy groceries');
await page.getByPlaceholder('What needs to be done?').press('Enter');
await expect(page.getByText('Buy groceries')).toBeVisible();
// @end-block

// @scenario: Complete a todo item
// @block: CompleteTodoItem
// @data: todoText = "Buy groceries"
await page.getByRole('checkbox', { name: 'Buy groceries' }).check();
await page.getByRole('link', { name: 'Completed' }).click();
await expect(page.getByText('Buy groceries')).toBeVisible();
// @end-block
```

**After `npm run convert`**, the agent produces:

`src/blocks/generated/AddTodoItemBlock.ts`
```typescript
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
```

`tests/generated/my-test.data.json`
```json
{
  "scenarios": [
    {
      "name": "Add a todo item",
      "steps": [
        { "block": "AddTodoItem", "data": { "todoText": "Buy groceries" } }
      ]
    },
    {
      "name": "Complete a todo item",
      "steps": [
        { "block": "AddTodoItem",      "data": { "todoText": "Buy groceries" } },
        { "block": "CompleteTodoItem", "data": { "todoText": "Buy groceries" } }
      ]
    }
  ]
}
```

`tests/generated/my-test.spec.ts`
```typescript
import { test } from '@playwright/test';
import { DataDrivenRunner } from '../../src/runner/DataDrivenRunner';
import type { TestDataFile } from '../../src/runner/DataDrivenRunner';
import testData from './my-test.data.json';

import '../../src/blocks/generated/AddTodoItemBlock';
import '../../src/blocks/generated/CompleteTodoItemBlock';

const runner = new DataDrivenRunner();

for (const scenario of (testData as unknown as TestDataFile).scenarios) {
  test(scenario.name, async ({ page }) => {
    await runner.run(page, scenario.steps);
  });
}
```

---

## LLM Provider Interface

All providers implement `src/agents/base/LLMAgent.ts`:

```typescript
export interface LLMAgent {
  complete(messages: LLMMessage[]): Promise<string>;
}
```

### Built-in Providers

| Provider  | File                              | Default model     | Env vars              |
|-----------|-----------------------------------|-------------------|-----------------------|
| anthropic | `providers/AnthropicAgent.ts`     | claude-sonnet-4-6 | `ANTHROPIC_API_KEY`   |
| openai    | `providers/OpenAIAgent.ts`        | gpt-4o            | `OPENAI_API_KEY`      |
| ollama    | `providers/OllamaAgent.ts`        | llama3            | `OLLAMA_BASE_URL`     |

Configure via `.env` (copy `.env.example`):

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Switching providers

```bash
# Groq (fast, OpenAI-compatible)
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk-...
LLM_MODEL=llama3-70b-8192

# Local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama3
```

### Adding a new provider

1. Create `src/agents/providers/MyProviderAgent.ts` implementing `LLMAgent`
2. Add a `case 'myprovider':` in `src/agents/AgentFactory.ts`
3. Set `LLM_PROVIDER=myprovider` in `.env`

No other files change.

---

## Quick-start

```bash
cd playwright-framework
cp .env.example .env            # add your API key
npm install
npm run install:browsers

# Record a test
npm run record https://your-app.com

# Annotate recordings/my-test.recording.ts with @block/@data tags, then:
npm run convert recordings/my-test.recording.ts

# Run the generated test
npx playwright test tests/generated/my-test.spec.ts
```
