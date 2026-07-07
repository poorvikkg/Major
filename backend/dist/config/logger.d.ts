/**
 * logger.ts
 * Creates a Pino logger instance.
 * In development mode, uses pino-pretty for human-readable output.
 * In production, outputs structured JSON for log aggregators.
 */
import pino from 'pino';
export declare const logger: pino.Logger<never, boolean>;
//# sourceMappingURL=logger.d.ts.map