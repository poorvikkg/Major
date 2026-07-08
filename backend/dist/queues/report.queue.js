"use strict";
/**
 * report.queue.ts
 * BullMQ queue for report generation jobs (PDF, daily, weekly).
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.reportQueue = exports.REPORT_QUEUE_NAME = void 0;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
exports.REPORT_QUEUE_NAME = 'report-generation';
exports.reportQueue = new bullmq_1.Queue(exports.REPORT_QUEUE_NAME, {
    connection: redis_1.redisConnectionOptions,
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
//# sourceMappingURL=report.queue.js.map