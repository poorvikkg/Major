/**
 * report.queue.ts
 * BullMQ queue for report generation jobs (PDF, daily, weekly).
 */

import { Queue } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import type { ReportJobData } from '../types/queue.types';

export const REPORT_QUEUE_NAME = 'report-generation';

export const reportQueue = new Queue<ReportJobData>(REPORT_QUEUE_NAME, {
  connection: redisConnectionOptions,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 3000, // 3 s → 6 s → 12 s (reports are heavier)
    },
    removeOnComplete: { count: 50 },
    removeOnFail: { count: 25 },
  },
});
