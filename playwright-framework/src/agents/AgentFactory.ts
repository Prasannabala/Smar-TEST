import { LLMAgent } from './base/LLMAgent';

/**
 * Creates an LLMAgent based on the LLM_PROVIDER environment variable.
 *
 * Supported values:
 *   anthropic  (default) — Claude via @anthropic-ai/sdk
 *   openai               — OpenAI-compatible (OpenAI, Groq, LM Studio, etc.)
 *   ollama               — Local Ollama instance
 *
 * The model can be overridden with LLM_MODEL.
 * See .env.example for all configuration options.
 */
export function createAgent(): LLMAgent {
  const provider = (process.env.LLM_PROVIDER ?? 'anthropic').toLowerCase().trim();
  const model = process.env.LLM_MODEL?.trim();

  switch (provider) {
    case 'anthropic': {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { AnthropicAgent } = require('./providers/AnthropicAgent') as typeof import('./providers/AnthropicAgent');
      return model ? new AnthropicAgent(model) : new AnthropicAgent();
    }
    case 'openai': {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { OpenAIAgent } = require('./providers/OpenAIAgent') as typeof import('./providers/OpenAIAgent');
      return model ? new OpenAIAgent(model) : new OpenAIAgent();
    }
    case 'ollama': {
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { OllamaAgent } = require('./providers/OllamaAgent') as typeof import('./providers/OllamaAgent');
      return model ? new OllamaAgent(model) : new OllamaAgent();
    }
    default:
      throw new Error(
        `Unknown LLM_PROVIDER: '${provider}'. ` +
        `Valid options: anthropic, openai, ollama`
      );
  }
}
