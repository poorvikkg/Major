/**
 * workers/index.ts
 * Central orchestrator for all BullMQ workers.
 * Call startWorkers() once at application startup and stopWorkers() on shutdown.
 */
/**
 * Initialise all four workers and register them for graceful shutdown.
 * Safe to call multiple times — subsequent calls are no-ops.
 */
export declare function startWorkers(): void;
/**
 * Gracefully close all workers.
 * Waits for in-progress jobs to finish before shutting down.
 */
export declare function stopWorkers(): Promise<void>;
//# sourceMappingURL=index.d.ts.map