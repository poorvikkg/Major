"use strict";
/**
 * notification.worker.ts
 * Processes jobs from the notification queue.
 * Handles: email, sms, push, socket
 * High concurrency (5) because notification delivery is mostly I/O-bound.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createNotificationWorker = createNotificationWorker;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
const notification_queue_1 = require("../queues/notification.queue");
const logger_1 = require("../config/logger");
const CONCURRENCY = 5;
// ── Job Handlers ────────────────────────────────────────────
async function sendEmail(job) {
    logger_1.logger.info({ jobId: job.id, destination: job.data.destination }, 'Sending email notification');
    await job.updateProgress(50);
    // e.g. await emailService.send({ to: job.data.destination, subject: job.data.subject, body: job.data.body });
    await job.updateProgress(100);
    return { success: true, message: 'Email sent', data: { destination: job.data.destination } };
}
async function sendSms(job) {
    logger_1.logger.info({ jobId: job.id, destination: job.data.destination }, 'Sending SMS notification');
    await job.updateProgress(50);
    // e.g. await smsService.send({ to: job.data.destination, message: job.data.body });
    await job.updateProgress(100);
    return { success: true, message: 'SMS sent', data: { destination: job.data.destination } };
}
async function sendPush(job) {
    logger_1.logger.info({ jobId: job.id, recipientId: job.data.recipientId }, 'Sending push notification');
    await job.updateProgress(50);
    // e.g. await pushService.send({ token: job.data.destination, title: job.data.subject, body: job.data.body });
    await job.updateProgress(100);
    return { success: true, message: 'Push notification sent', data: { recipientId: job.data.recipientId } };
}
async function sendSocketNotification(job) {
    logger_1.logger.info({ jobId: job.id, recipientId: job.data.recipientId, event: job.data.socketEvent }, 'Emitting socket event');
    await job.updateProgress(50);
    // e.g. io.to(job.data.recipientId).emit(job.data.socketEvent ?? 'notification', { body: job.data.body });
    await job.updateProgress(100);
    return { success: true, message: 'Socket event emitted', data: { recipientId: job.data.recipientId } };
}
// ── Router ──────────────────────────────────────────────────
async function processJob(job) {
    switch (job.data.jobType) {
        case 'email':
            return sendEmail(job);
        case 'sms':
            return sendSms(job);
        case 'push':
            return sendPush(job);
        case 'socket':
            return sendSocketNotification(job);
        default:
            throw new Error(`Unknown notification job type: ${job.data.jobType}`);
    }
}
// ── Worker Instance ─────────────────────────────────────────
function createNotificationWorker() {
    const worker = new bullmq_1.Worker(notification_queue_1.NOTIFICATION_QUEUE_NAME, processJob, {
        connection: redis_1.redisConnectionOptions,
        concurrency: CONCURRENCY,
    });
    worker.on('active', (job) => {
        logger_1.logger.info({ jobId: job.id, jobType: job.data.jobType }, '[notification-worker] Job started');
    });
    worker.on('completed', (job, result) => {
        logger_1.logger.info({ jobId: job.id, result }, '[notification-worker] Job completed');
    });
    worker.on('failed', (job, err) => {
        logger_1.logger.error({ jobId: job?.id, err }, '[notification-worker] Job failed');
    });
    worker.on('error', (err) => {
        logger_1.logger.error({ err }, '[notification-worker] Worker error');
    });
    return worker;
}
//# sourceMappingURL=notification.worker.js.map