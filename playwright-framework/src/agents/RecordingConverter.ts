import * as fs from 'fs';
import * as path from 'path';
import { CommentAnnotationParser } from './CommentAnnotationParser';
import { TestCodeGenerator } from './TestCodeGenerator';
import { createAgent } from './AgentFactory';
import { logger } from '../utils/logger';

/**
 * Orchestrates the full recording → data-driven test pipeline:
 *   1. CommentAnnotationParser  — reads & parses @block/@data/@param tags (no LLM)
 *   2. TestCodeGenerator        — calls LLM agent to produce spec + data files
 *
 * Usage:
 *   const converter = new RecordingConverter();
 *   await converter.convert('recordings/my-test.recording.ts', 'tests/generated');
 */
export class RecordingConverter {
  private parser = new CommentAnnotationParser();
  private generator: TestCodeGenerator;

  constructor() {
    require('dotenv').config();
    this.generator = new TestCodeGenerator(createAgent());
  }

  async convert(recordingPath: string, outputDir: string): Promise<void> {
    const absRecording = path.resolve(recordingPath);
    const absOutputDir = path.resolve(outputDir);

    if (!fs.existsSync(absRecording)) {
      throw new Error(`Recording file not found: ${absRecording}`);
    }

    logger.info(`Parsing: ${absRecording}`);
    const annotated = this.parser.parse(absRecording);

    if (annotated.segments.length === 0) {
      throw new Error(
        'No @block annotations found in the recording.\n' +
        'Add "// @block: MyBlockName" before each section and "// @end-block" after it.\n' +
        'See recordings/example-todo.recording.ts for an example.'
      );
    }

    logger.info(`Found ${annotated.segments.length} block segment(s).`);

    // Derive a safe test name from the filename (strip .recording.ts)
    const baseName = path.basename(absRecording).replace(/\.recording\.ts$/, '').replace(/\.ts$/, '');
    const testName = baseName.replace(/[^a-z0-9-]/gi, '-').toLowerCase();

    const generated = await this.generator.generate(annotated, testName);

    fs.mkdirSync(absOutputDir, { recursive: true });

    const dataPath = path.join(absOutputDir, `${testName}.data.json`);
    const specPath = path.join(absOutputDir, `${testName}.spec.ts`);

    fs.writeFileSync(dataPath, generated.dataFile, 'utf-8');
    fs.writeFileSync(specPath, generated.specFile, 'utf-8');

    logger.success(`Data file : ${dataPath}`);
    logger.success(`Spec file : ${specPath}`);
    logger.success(`Run tests : npx playwright test ${specPath}`);
  }
}
