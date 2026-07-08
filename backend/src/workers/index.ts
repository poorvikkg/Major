/**
 * workers/index.ts
 * Central orchestrator for all BullMQ workers.
 * Call startWorkers() once at application startup and stopWorkers() on shutdown.
 */

import { type Worker } from 'bullmq';
import { createVideoWorker } from './video.worker';
import { createComplaintWorker } from './complaint.worker';
import { createReportWorker } from './report.worker';
import { createNotificationWorker } from './notification.worker';
import { logger } from '../config/logger';

/** Holds references to all active workers so they can be stopped cleanly */
const activeWorkers: Worker[] = [];

/**
 * Initialise all four workers and register them for graceful shutdown.
 * Safe to call multiple times — subsequent calls are no-ops.
 */
export function startWorkers(): void {
  if (activeWorkers.length > 0) return; // already started

  activeWorkers.push(
    createVideoWorker(),
    createComplaintWorker(),
    createReportWorker(),
    createNotificationWorker(),
  );

  logger.info(`BullMQ: ${activeWorkers.length} workers started`);
}

/**
 * Gracefully close all workers.
 * Waits for in-progress jobs to finish before shutting down.
 */
export async function stopWorkers(): Promise<void> {
  logger.info('BullMQ: stopping all workers...');
  await Promise.all(activeWorkers.map((w) => w.close()));
  activeWorkers.length = 0;
  logger.info('BullMQ: all workers stopped');
}
