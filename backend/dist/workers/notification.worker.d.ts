/**
 * notification.worker.ts
 * Processes jobs from the notification queue.
 * Handles: email, sms, push, socket
 * High concurrency (5) because notification delivery is mostly I/O-bound.
 */
import { Worker } from 'bullmq';
import type { NotificationJobData, JobResult } from '../types/queue.types';
export declare function createNotificationWorker(): Worker<NotificationJobData, JobResult>;
//# sourceMappingURL=notification.worker.d.ts.map