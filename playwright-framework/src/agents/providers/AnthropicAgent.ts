import Anthropic from '@anthropic-ai/sdk';
import { LLMAgent, LLMMessage } from '../base/LLMAgent';

/**
 * Claude provider via @anthropic-ai/sdk.
 * Uses prompt caching on the system message to reduce cost on repeated conversions.
 * Default model: claude-sonnet-4-6. Override with LLM_MODEL env var.
 */
export class AnthropicAgent implements LLMAgent {
  private client: Anthropic;
  private model: string;

  constructor(model = 'claude-sonnet-4-6') {
    if (!process.env.ANTHROPIC_API_KEY) {
      throw new Error('ANTHROPIC_API_KEY is not set. Add it to your .env file.');
    }
    this.client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    this.model = model;
  }

  async complete(messages: LLMMessage[]): Promise<string> {
    const systemMsg = messages.find(m => m.role === 'system');
    const conversation = messages.filter(m => m.role !== 'system');

    const response = await this.client.messages.create({
      model: this.model,
      max_tokens: 4096,
      ...(systemMsg && {
        system: [
          {
            type: 'text' as const,
            text: systemMsg.content,
            cache_control: { type: 'ephemeral' as const },
          },
        ],
      }),
      messages: conversation.map(m => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      })),
    });

    const block = response.content[0];
    if (block.type !== 'text') {
      throw new Error(`Unexpected Anthropic response type: ${block.type}`);
    }
    return block.text;
  }
}
