/**
 * notification.queue.ts
 * BullMQ queue for notification delivery (email, SMS, push, socket).
 * Notifications are best-effort — only 1 retry to avoid spam.
 */

import { Queue } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import type { NotificationJobData } from '../types/queue.types';

export const NOTIFICATION_QUEUE_NAME = 'notification';

export const notificationQueue = new Queue<NotificationJobData>(NOTIFICATION_QUEUE_NAME, {
  connection: redisConnectionOptions,
  defaultJobOptions: {
    attempts: 1, // best-effort; avoid duplicate notifications
    removeOnComplete: { count: 200 },
    removeOnFail: { count: 100 },
  },
});
