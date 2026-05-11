import { Page } from '@playwright/test';

export type BlockData = Record<string, unknown>;

export abstract class Block {
  abstract readonly name: string;
  abstract readonly requiredParams: string[];

  abstract execute(page: Page, data: BlockData): Promise<void>;

  protected assertParams(data: BlockData): void {
    for (const param of this.requiredParams) {
      if (!(param in data) || data[param] === undefined || data[param] === null) {
        throw new Error(
          `Block '${this.name}' is missing required param: '${param}'. ` +
          `Received keys: [${Object.keys(data).join(', ')}]`
        );
      }
    }
  }
}
