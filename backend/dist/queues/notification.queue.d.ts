/**
 * notification.queue.ts
 * BullMQ queue for notification delivery (email, SMS, push, socket).
 * Notifications are best-effort — only 1 retry to avoid spam.
 */
import { Queue } from 'bullmq';
import type { NotificationJobData } from '../types/queue.types';
export declare const NOTIFICATION_QUEUE_NAME = "notification";
export declare const notificationQueue: Queue<NotificationJobData, any, string, NotificationJobData, any, string>;
//# sourceMappingURL=notification.queue.d.ts.map