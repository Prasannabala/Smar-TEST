import { Block } from './Block';

type BlockConstructor = new () => Block;

class BlockRegistryClass {
  private registry = new Map<string, BlockConstructor>();

  register(name: string, ctor: BlockConstructor): void {
    this.registry.set(name, ctor);
  }

  get(name: string): Block {
    const Ctor = this.registry.get(name);
    if (!Ctor) {
      const available = [...this.registry.keys()].join(', ');
      throw new Error(
        `Block '${name}' not found in registry.\n` +
        `Available blocks: [${available}]\n` +
        `Make sure you import the block file before using it.`
      );
    }
    return new Ctor();
  }

  list(): string[] {
    return [...this.registry.keys()].sort();
  }

  has(name: string): boolean {
    return this.registry.has(name);
  }
}

export const BlockRegistry = new BlockRegistryClass();
