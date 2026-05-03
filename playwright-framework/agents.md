# Agents — Role Reference & Provider Guide

This document describes every agent in the framework, its role, when it runs,
and how to add or swap a provider.

---

## Agent Roles

### 1. CommentAnnotationParser
**File:** `src/agents/CommentAnnotationParser.ts`
**Type:** Pure TypeScript (no LLM)

Reads an annotated Playwright recording and extracts structured segments from
the `// @` comment tags. This runs first, before any LLM call, so it is fast
and cost-free regardless of provider.

**Output:** `AnnotatedRecording` — an array of `ScenarioSegment` objects, each
containing the block name, scenario name, code steps, data entries, and params.

---

### 2. TestCodeGenerator
**File:** `src/agents/TestCodeGenerator.ts`
**Type:** LLM-powered (provider-agnostic via `LLMAgent` interface)

Receives the parsed `AnnotatedRecording` and calls the configured LLM to produce:
- `<testName>.data.json` — scenario definitions following the step-based schema
- `<testName>.spec.ts` — Playwright test file using `DataDrivenRunner` + LEGO blocks

The system prompt is written once; the provider is injected at runtime via `AgentFactory`.
Prompt caching is enabled on Anthropic to reduce cost on repeated runs.

---

### 3. RecordingConverter
**File:** `src/agents/RecordingConverter.ts`
**Type:** Orchestrator

Ties the pipeline together:
```
recording file
     │
     ▼
CommentAnnotationParser  ──(no LLM)──►  AnnotatedRecording
     │
     ▼
TestCodeGenerator        ──(LLM call)──► { dataFile, specFile }
     │
     ▼
writes tests/generated/<testName>.data.json
writes tests/generated/<testName>.spec.ts
```

---

## LLM Provider Interface

All providers implement the same interface (`src/agents/base/LLMAgent.ts`):

```typescript
export interface LLMAgent {
  complete(messages: LLMMessage[]): Promise<string>;
}
```

`messages` is an array of `{ role: 'system' | 'user' | 'assistant', content: string }`.

---

## Built-in Providers

| Provider  | File                              | Default model      | Env vars required         |
|-----------|-----------------------------------|--------------------|---------------------------|
| anthropic | `providers/AnthropicAgent.ts`     | claude-sonnet-4-6  | `ANTHROPIC_API_KEY`       |
| openai    | `providers/OpenAIAgent.ts`        | gpt-4o             | `OPENAI_API_KEY`          |
| ollama    | `providers/OllamaAgent.ts`        | llama3             | `OLLAMA_BASE_URL` (opt)   |

Configure via `.env`:

```bash
LLM_PROVIDER=anthropic       # anthropic | openai | ollama
LLM_MODEL=claude-sonnet-4-6  # optional override
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Switching Providers

```bash
# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Use Groq (OpenAI-compatible)
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk-...
LLM_MODEL=llama3-70b-8192

# Use local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama3
# OLLAMA_BASE_URL=http://localhost:11434  (default)
```

---

## Adding a New Provider

1. Create `src/agents/providers/MyProviderAgent.ts`:

```typescript
import { LLMAgent, LLMMessage } from '../base/LLMAgent';

export class MyProviderAgent implements LLMAgent {
  async complete(messages: LLMMessage[]): Promise<string> {
    // Call your provider API here
    // Return the assistant reply as a string
  }
}
```

2. Register it in `src/agents/AgentFactory.ts`:

```typescript
case 'myprovider': {
  const { MyProviderAgent } = require('./providers/MyProviderAgent');
  return new MyProviderAgent();
}
```

3. Set in `.env`:

```bash
LLM_PROVIDER=myprovider
```

That's all. No other files need to change.

---

## Comment Annotation Tag Reference

Add these comments to your Playwright codegen recording before converting it.

| Tag | Placement | Effect |
|-----|-----------|--------|
| `// @scenario: Name` | standalone line | Names the next test (used as Playwright `test()` title) |
| `// @block: Name` | standalone line | Opens a named LEGO block segment |
| `// @end-block` | standalone line | Closes the current segment |
| `// @data: key = "value"` | standalone line above code | Declares a data parameter extracted into the JSON |
| `await ...;  // @param: key` | inline on code line | Marks an inline value as parameterised |
| `// @step: Description` | standalone line | Labels a logical step (for reporting only, not required) |

### Minimal example

```typescript
// @scenario: Login with valid credentials
// @block: LoginFlow
await page.goto('https://app.example.com/login');  // @param: baseUrl
// @data: email = "alice@example.com"
await page.getByLabel('Email').fill('alice@example.com');
// @data: password = "secret123"
await page.getByLabel('Password').fill('secret123');
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL('https://app.example.com/dashboard');  // @param: expectedUrl
// @end-block
```

After `npm run convert recordings/my-login.recording.ts` the framework produces:

**`tests/generated/my-login.data.json`**
```json
{
  "scenarios": [
    {
      "name": "Login with valid credentials",
      "steps": [
        { "block": "Navigate",   "data": { "url": "https://app.example.com/login" } },
        { "block": "Fill",       "data": { "selector": "[aria-label='Email']", "value": "alice@example.com" } },
        { "block": "Fill",       "data": { "selector": "[aria-label='Password']", "value": "secret123" } },
        { "block": "Click",      "data": { "selector": "button:has-text('Sign in')" } },
        { "block": "AssertUrl",  "data": { "url": "https://app.example.com/dashboard" } }
      ]
    }
  ]
}
```

**`tests/generated/my-login.spec.ts`**
```typescript
import { test } from '@playwright/test';
import { DataDrivenRunner } from '../../src/runner/DataDrivenRunner';
import type { TestDataFile } from '../../src/runner/DataDrivenRunner';
import testData from './my-login.data.json';

import '../../src/blocks/actions/NavigateBlock';
import '../../src/blocks/actions/FillBlock';
import '../../src/blocks/actions/ClickBlock';
import '../../src/blocks/assertions/UrlAssertBlock';

const runner = new DataDrivenRunner();

for (const scenario of (testData as unknown as TestDataFile).scenarios) {
  test(scenario.name, async ({ page }) => {
    await runner.run(page, scenario.steps);
  });
}
```

To add more data rows (true data-driven), duplicate the scenario object in the
JSON and change only the data values. The test file stays unchanged.
