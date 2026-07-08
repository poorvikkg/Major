"use strict";
/**
 * notification.queue.ts
 * BullMQ queue for notification delivery (email, SMS, push, socket).
 * Notifications are best-effort — only 1 retry to avoid spam.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.notificationQueue = exports.NOTIFICATION_QUEUE_NAME = void 0;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
exports.NOTIFICATION_QUEUE_NAME = 'notification';
exports.notificationQueue = new bullmq_1.Queue(exports.NOTIFICATION_QUEUE_NAME, {
    connection: redis_1.redisConnectionOptions,
    defaultJobOptions: {
        attempts: 1, // best-effort; avoid duplicate notifications
        removeOnComplete: { count: 200 },
        removeOnFail: { count: 100 },
    },
});
//# sourceMappingURL=notification.queue.js.map