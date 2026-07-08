"use strict";
/**
 * video.worker.ts
 * Processes jobs from the video-processing queue.
 * Handles: process-video, analyze-cctv
 *
 * Each handler is a small focused function — easy to extend independently.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createVideoWorker = createVideoWorker;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
const video_queue_1 = require("../queues/video.queue");
const logger_1 = require("../config/logger");
/** Concurrency: process 2 video jobs in parallel */
const CONCURRENCY = 2;
// ── Job Handlers ────────────────────────────────────────────
async function processVideo(job) {
    logger_1.logger.info({ jobId: job.id, objectKey: job.data.objectKey }, 'Processing uploaded video');
    // Step 1 — validate input (25%)
    await job.updateProgress(25);
    if (!job.data.objectKey) {
        throw new Error('objectKey is required for video processing');
    }
    // Step 2 — placeholder: call your video processing service here (50%)
    await job.updateProgress(50);
    // e.g. await videoService.transcode(job.data.objectKey);
    // Step 3 — store result metadata (75%)
    await job.updateProgress(75);
    // e.g. await VideoRepository.updateStatus(job.data.videoId, 'processed');
    await job.updateProgress(100);
    return { success: true, message: 'Video processed successfully', data: { videoId: job.data.videoId } };
}
async function analyzeCctv(job) {
    logger_1.logger.info({ jobId: job.id, cameraId: job.data.cameraId }, 'Analysing CCTV recording');
    await job.updateProgress(30);
    // e.g. await cctvAnalysisService.analyze(job.data.objectKey, job.data.cameraId);
    await job.updateProgress(80);
    // e.g. await CameraRepository.saveAnalysisResult(job.data.cameraId, results);
    await job.updateProgress(100);
    return { success: true, message: 'CCTV analysis complete', data: { cameraId: job.data.cameraId } };
}
// ── Router ──────────────────────────────────────────────────
async function processJob(job) {
    switch (job.data.jobType) {
        case 'process-video':
            return processVideo(job);
        case 'analyze-cctv':
            return analyzeCctv(job);
        default:
            throw new Error(`Unknown video job type: ${job.data.jobType}`);
    }
}
// ── Worker Instance ─────────────────────────────────────────
function createVideoWorker() {
    const worker = new bullmq_1.Worker(video_queue_1.VIDEO_QUEUE_NAME, processJob, {
        connection: redis_1.redisConnectionOptions,
        concurrency: CONCURRENCY,
    });
    worker.on('active', (job) => {
        logger_1.logger.info({ jobId: job.id, jobType: job.data.jobType }, '[video-worker] Job started');
    });
    worker.on('completed', (job, result) => {
        logger_1.logger.info({ jobId: job.id, result }, '[video-worker] Job completed');
    });
    worker.on('failed', (job, err) => {
        logger_1.logger.error({ jobId: job?.id, err }, '[video-worker] Job failed');
    });
    worker.on('error', (err) => {
        logger_1.logger.error({ err }, '[video-worker] Worker error');
    });
    return worker;
}
//# sourceMappingURL=video.worker.js.map