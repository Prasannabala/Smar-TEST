const c = {
  reset: '\x1b[0m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  bold: '\x1b[1m',
};

export const logger = {
  info: (msg: string) =>
    console.log(`${c.cyan}[INFO]${c.reset}  ${msg}`),
  success: (msg: string) =>
    console.log(`${c.green}${c.bold}[OK]${c.reset}    ${msg}`),
  warn: (msg: string) =>
    console.warn(`${c.yellow}[WARN]${c.reset}  ${msg}`),
  error: (msg: string) =>
    console.error(`${c.red}[ERROR]${c.reset} ${msg}`),
};
