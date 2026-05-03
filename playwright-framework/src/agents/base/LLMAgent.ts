export type MessageRole = 'system' | 'user' | 'assistant';

export interface LLMMessage {
  role: MessageRole;
  content: string;
}

/**
 * Provider-agnostic interface for LLM completion.
 * Implement this to add a new provider (Anthropic, OpenAI, Ollama, Groq, etc.)
 * and register it in AgentFactory.ts.
 */
export interface LLMAgent {
  complete(messages: LLMMessage[]): Promise<string>;
}
