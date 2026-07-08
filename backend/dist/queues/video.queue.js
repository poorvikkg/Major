"use strict";
/**
 * video.queue.ts
 * BullMQ queue for video processing jobs (uploads, CCTV analysis).
 * Controllers call videoQueue.add() to enqueue work without blocking the request.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.videoQueue = exports.VIDEO_QUEUE_NAME = void 0;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
exports.VIDEO_QUEUE_NAME = 'video-processing';
exports.videoQueue = new bullmq_1.Queue(exports.VIDEO_QUEUE_NAME, {
    connection: redis_1.redisConnectionOptions,
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
//# sourceMappingURL=video.queue.js.map