#!/usr/bin/env ts-node
/**
 * CLI: Convert an annotated Playwright recording into a data-driven LEGO block test.
 *
 * Usage:
 *   npm run convert <recording-file> [output-dir]
 *
 * Examples:
 *   npm run convert recordings/login.recording.ts
 *   npm run convert recordings/checkout.recording.ts tests/generated
 *
 * Requirements:
 *   - Copy .env.example to .env and set LLM_PROVIDER + API key
 *   - The recording file must have @block / @end-block annotations
 */

import { RecordingConverter } from '../src/agents/RecordingConverter';
import { logger } from '../src/utils/logger';

async function main(): Promise<void> {
  const [, , recordingPath, outputDir = 'tests/generated'] = process.argv;

  if (!recordingPath) {
    logger.error('Usage: npm run convert <recording-file> [output-dir]');
    logger.error('');
    logger.error('Examples:');
    logger.error('  npm run convert recordings/my-test.recording.ts');
    logger.error('  npm run convert recordings/my-test.recording.ts tests/e2e/generated');
    process.exit(1);
  }

  const converter = new RecordingConverter();

  try {
    await converter.convert(recordingPath, outputDir);
  } catch (err) {
    logger.error(err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
