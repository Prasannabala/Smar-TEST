import * as fs from 'fs';
import * as path from 'path';
import { CommentAnnotationParser } from './CommentAnnotationParser';
import { TestCodeGenerator } from './TestCodeGenerator';
import { createAgent } from './AgentFactory';
import { logger } from '../utils/logger';

/**
 * Orchestrates the full recording → business LEGO blocks pipeline:
 *
 *   1. CommentAnnotationParser  — extracts @block/@data/@scenario tags (no LLM, instant)
 *   2. TestCodeGenerator        — calls LLM to:
 *        a) generate a TypeScript Block class for each unique @block name
 *        b) generate <testName>.data.json  with business-level params
 *        c) generate <testName>.spec.ts    that assembles blocks like LEGO
 *
 * Output locations:
 *   src/blocks/generated/<BlockName>Block.ts   ← business block classes
 *   tests/generated/<testName>.data.json       ← scenario data
 *   tests/generated/<testName>.spec.ts         ← data-driven spec
 */
export class RecordingConverter {
  private parser = new CommentAnnotationParser();
  private generator: TestCodeGenerator;
  private frameworkRoot: string;

  constructor() {
    require('dotenv').config();
    this.generator = new TestCodeGenerator(createAgent());
    // Resolve the framework root relative to this file's location at runtime
    this.frameworkRoot = path.resolve(__dirname, '../../..');
  }

  async convert(recordingPath: string, outputDir: string): Promise<void> {
    const absRecording = path.resolve(recordingPath);
    const absOutputDir = path.resolve(outputDir);
    const generatedBlocksDir = path.join(this.frameworkRoot, 'src', 'blocks', 'generated');

    if (!fs.existsSync(absRecording)) {
      throw new Error(`Recording file not found: ${absRecording}`);
    }

    logger.info(`Parsing: ${absRecording}`);
    const annotated = this.parser.parse(absRecording);

    if (annotated.segments.length === 0) {
      throw new Error(
        'No @block annotations found in the recording.\n' +
        'Add  // @block: BusinessActionName  before each section\n' +
        'and  // @end-block  after it.\n' +
        'See recordings/example-todo.recording.ts for a complete example.'
      );
    }

    const uniqueBlocks = [...new Set(annotated.segments.map(s => s.blockName))];
    logger.info(
      `Found ${annotated.segments.length} segment(s) across ${uniqueBlocks.length} unique block(s): ` +
      `[${uniqueBlocks.join(', ')}]`
    );

    const baseName = path
      .basename(absRecording)
      .replace(/\.recording\.ts$/, '')
      .replace(/\.ts$/, '');
    const testName = baseName.replace(/[^a-z0-9-]/gi, '-').toLowerCase();

    const generated = await this.generator.generate(annotated, testName);

    // ── Write business block classes ──────────────────────────────────────
    fs.mkdirSync(generatedBlocksDir, { recursive: true });

    for (const [fileName, content] of Object.entries(generated.blockFiles)) {
      const blockPath = path.join(generatedBlocksDir, fileName);
      fs.writeFileSync(blockPath, content, 'utf-8');
      logger.success(`Block class: ${blockPath}`);
    }

    // ── Write spec + data files ───────────────────────────────────────────
    fs.mkdirSync(absOutputDir, { recursive: true });

    const dataPath = path.join(absOutputDir, `${testName}.data.json`);
    const specPath = path.join(absOutputDir, `${testName}.spec.ts`);

    fs.writeFileSync(dataPath, generated.dataFile, 'utf-8');
    fs.writeFileSync(specPath, generated.specFile, 'utf-8');

    logger.success(`Data file : ${dataPath}`);
    logger.success(`Spec file : ${specPath}`);
    logger.success(`Run test  : npx playwright test ${specPath}`);
  }
}
