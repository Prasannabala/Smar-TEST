import OpenAI from 'openai';
import { LLMAgent, LLMMessage } from '../base/LLMAgent';

/**
 * OpenAI-compatible provider.
 * Works with OpenAI, Groq, Together AI, LM Studio, and any OpenAI-compatible API.
 * Set OPENAI_BASE_URL to point at a different endpoint.
 * Default model: gpt-4o. Override with LLM_MODEL env var.
 */
export class OpenAIAgent implements LLMAgent {
  private client: OpenAI;
  private model: string;

  constructor(model = 'gpt-4o') {
    this.client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY ?? 'not-set',
      baseURL: process.env.OPENAI_BASE_URL,
    });
    this.model = model;
  }

  async complete(messages: LLMMessage[]): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: this.model,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
    });
    return response.choices[0]?.message?.content ?? '';
  }
}
