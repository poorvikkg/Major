/**
 * complaint.queue.ts
 * BullMQ queue for AI complaint processing jobs (speech-to-text, summarisation, extraction).
 */

import { Queue } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import type { ComplaintJobData } from '../types/queue.types';

export const COMPLAINT_QUEUE_NAME = 'complaint-ai';

export const complaintQueue = new Queue<ComplaintJobData>(COMPLAINT_QUEUE_NAME, {
  connection: redisConnectionOptions,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 1000, // 1 s → 2 s → 4 s
    },
    removeOnComplete: { count: 100 },
    removeOnFail: { count: 50 },
  },
});
