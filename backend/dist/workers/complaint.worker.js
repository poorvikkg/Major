"use strict";
/**
 * complaint.worker.ts
 * Processes jobs from the complaint-ai queue.
 * Handles: speech-to-text, summarize-complaint, extract-information
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createComplaintWorker = createComplaintWorker;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
const complaint_queue_1 = require("../queues/complaint.queue");
const logger_1 = require("../config/logger");
const CONCURRENCY = 3;
// ── Job Handlers ────────────────────────────────────────────
async function speechToText(job) {
    logger_1.logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Transcribing audio');
    await job.updateProgress(30);
    // e.g. const transcript = await speechService.transcribe(job.data.payload, job.data.language);
    await job.updateProgress(80);
    // e.g. await ComplaintRepository.saveTranscript(job.data.complaintId, transcript);
    await job.updateProgress(100);
    return { success: true, message: 'Audio transcribed successfully', data: { complaintId: job.data.complaintId } };
}
async function summarizeComplaint(job) {
    logger_1.logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Summarising complaint');
    await job.updateProgress(40);
    // e.g. const summary = await aiService.summarize(job.data.payload);
    await job.updateProgress(80);
    // e.g. await ComplaintRepository.saveSummary(job.data.complaintId, summary);
    await job.updateProgress(100);
    return { success: true, message: 'Complaint summarised', data: { complaintId: job.data.complaintId } };
}
async function extractInformation(job) {
    logger_1.logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Extracting information');
    await job.updateProgress(50);
    // e.g. const entities = await aiService.extract(job.data.payload);
    await job.updateProgress(80);
    // e.g. await ComplaintRepository.saveEntities(job.data.complaintId, entities);
    await job.updateProgress(100);
    return { success: true, message: 'Information extracted', data: { complaintId: job.data.complaintId } };
}
// ── Router ──────────────────────────────────────────────────
async function processJob(job) {
    switch (job.data.jobType) {
        case 'speech-to-text':
            return speechToText(job);
        case 'summarize-complaint':
            return summarizeComplaint(job);
        case 'extract-information':
            return extractInformation(job);
        default:
            throw new Error(`Unknown complaint job type: ${job.data.jobType}`);
    }
}
// ── Worker Instance ─────────────────────────────────────────
function createComplaintWorker() {
    const worker = new bullmq_1.Worker(complaint_queue_1.COMPLAINT_QUEUE_NAME, processJob, {
        connection: redis_1.redisConnectionOptions,
        concurrency: CONCURRENCY,
    });
    worker.on('active', (job) => {
        logger_1.logger.info({ jobId: job.id, jobType: job.data.jobType }, '[complaint-worker] Job started');
    });
    worker.on('completed', (job, result) => {
        logger_1.logger.info({ jobId: job.id, result }, '[complaint-worker] Job completed');
    });
    worker.on('failed', (job, err) => {
        logger_1.logger.error({ jobId: job?.id, err }, '[complaint-worker] Job failed');
    });
    worker.on('error', (err) => {
        logger_1.logger.error({ err }, '[complaint-worker] Worker error');
    });
    return worker;
}
//# sourceMappingURL=complaint.worker.js.map