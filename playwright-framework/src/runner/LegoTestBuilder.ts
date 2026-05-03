import { BlockRegistry } from '../blocks/base/BlockRegistry';
import { BlockData } from '../blocks/base/Block';
import { Scenario } from './DataDrivenRunner';

/**
 * Validates a scenario's block names against the registry before test execution.
 * Throws early with a clear message if a block is missing or not imported.
 */
export class LegoTestBuilder {
  validate(scenario: Scenario): void {
    const missing = scenario.steps
      .map(s => s.block)
      .filter(name => !BlockRegistry.has(name));

    if (missing.length > 0) {
      throw new Error(
        `Scenario "${scenario.name}" references unregistered blocks: [${missing.join(', ')}].\n` +
        `Registered blocks: [${BlockRegistry.list().join(', ')}].\n` +
        `Import the block file in your spec to register it.`
      );
    }
  }

  /**
   * Builds a flat data map from a shared data object + per-step overrides.
   * Useful for parameterised scenarios where most data is shared but some steps differ.
   */
  mergeData(shared: BlockData, overrides: BlockData = {}): BlockData {
    return { ...shared, ...overrides };
  }
}
