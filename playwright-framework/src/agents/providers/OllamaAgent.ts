import { LLMAgent, LLMMessage } from '../base/LLMAgent';

interface OllamaResponse {
  message: { content: string };
}

/**
 * Local Ollama provider via REST API.
 * Requires Ollama running at OLLAMA_BASE_URL (default: http://localhost:11434).
 * Default model: llama3. Override with LLM_MODEL env var.
 * Install a model: ollama pull llama3
 */
export class OllamaAgent implements LLMAgent {
  private baseUrl: string;
  private model: string;

  constructor(model = 'llama3') {
    this.baseUrl = process.env.OLLAMA_BASE_URL ?? 'http://localhost:11434';
    this.model = model;
  }

  async complete(messages: LLMMessage[]): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: this.model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        stream: false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama request failed (${response.status}): ${response.statusText}`);
    }

    const json = (await response.json()) as OllamaResponse;
    return json.message.content;
  }
}
