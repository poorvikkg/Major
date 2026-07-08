/**
 * video.queue.ts
 * BullMQ queue for video processing jobs (uploads, CCTV analysis).
 * Controllers call videoQueue.add() to enqueue work without blocking the request.
 */

import { Queue } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import type { VideoJobData } from '../types/queue.types';

export const VIDEO_QUEUE_NAME = 'video-processing';

export const videoQueue = new Queue<VideoJobData>(VIDEO_QUEUE_NAME, {
  connection: redisConnectionOptions,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000, // 2 s → 4 s → 8 s
    },
    // Keep the last 100 completed and 50 failed jobs for inspection
    removeOnComplete: { count: 100 },
    removeOnFail: { count: 50 },
  },
});
