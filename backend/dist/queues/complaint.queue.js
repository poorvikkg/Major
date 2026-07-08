"use strict";
/**
 * complaint.queue.ts
 * BullMQ queue for AI complaint processing jobs (speech-to-text, summarisation, extraction).
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.complaintQueue = exports.COMPLAINT_QUEUE_NAME = void 0;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
exports.COMPLAINT_QUEUE_NAME = 'complaint-ai';
exports.complaintQueue = new bullmq_1.Queue(exports.COMPLAINT_QUEUE_NAME, {
    connection: redis_1.redisConnectionOptions,
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
//# sourceMappingURL=complaint.queue.js.map