"use strict";
/**
 * job.controller.ts
 * Example controller showing the correct BullMQ pattern:
 *   Validate → Enqueue → Return 202 + Job ID
 *
 * Controllers never run long tasks; they delegate to workers via queues.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.enqueueVideoJob = enqueueVideoJob;
exports.enqueueComplaintJob = enqueueComplaintJob;
exports.enqueueReportJob = enqueueReportJob;
exports.enqueueNotificationJob = enqueueNotificationJob;
exports.getJobStatus = getJobStatus;
const video_queue_1 = require("../queues/video.queue");
const complaint_queue_1 = require("../queues/complaint.queue");
const report_queue_1 = require("../queues/report.queue");
const notification_queue_1 = require("../queues/notification.queue");
// ── Queue name → Queue instance map for the status endpoint ──
const queueMap = {
    'video-processing': video_queue_1.videoQueue,
    'complaint-ai': complaint_queue_1.complaintQueue,
    'report-generation': report_queue_1.reportQueue,
    notification: notification_queue_1.notificationQueue,
};
// ── Enqueue Handlers ────────────────────────────────────────
/**
 * POST /api/jobs/video
 * Body: { videoId, objectKey, requestedBy, jobType? }
 * Enqueues a video-processing job and returns 202 with the job ID.
 */
async function enqueueVideoJob(req, res, next) {
    try {
        const { videoId, objectKey, requestedBy, jobType = 'process-video' } = req.body;
        if (!videoId || !objectKey || !requestedBy) {
            res.status(400).json({ success: false, message: 'videoId, objectKey and requestedBy are required' });
            return;
        }
        const jobData = { jobType, videoId, objectKey, requestedBy };
        const job = await video_queue_1.videoQueue.add(jobType, jobData);
        res.status(202).json({
            success: true,
            message: 'Video job queued',
            jobId: job.id,
            queue: 'video-processing',
        });
    }
    catch (err) {
        next(err);
    }
}
/**
 * POST /api/jobs/complaint
 * Body: { complaintId, payload, jobType, language? }
 */
async function enqueueComplaintJob(req, res, next) {
    try {
        const { complaintId, payload, jobType = 'summarize-complaint', language } = req.body;
        if (!complaintId || !payload) {
            res.status(400).json({ success: false, message: 'complaintId and payload are required' });
            return;
        }
        const jobData = { jobType, complaintId, payload, language };
        const job = await complaint_queue_1.complaintQueue.add(jobType, jobData);
        res.status(202).json({ success: true, message: 'Complaint AI job queued', jobId: job.id, queue: 'complaint-ai' });
    }
    catch (err) {
        next(err);
    }
}
/**
 * POST /api/jobs/report
 * Body: { reportId, targetDate, requestedBy, jobType? }
 */
async function enqueueReportJob(req, res, next) {
    try {
        const { reportId, targetDate, requestedBy, jobType = 'generate-pdf' } = req.body;
        if (!reportId || !targetDate || !requestedBy) {
            res.status(400).json({ success: false, message: 'reportId, targetDate and requestedBy are required' });
            return;
        }
        const jobData = { jobType, reportId, targetDate, requestedBy };
        const job = await report_queue_1.reportQueue.add(jobType, jobData);
        res.status(202).json({ success: true, message: 'Report job queued', jobId: job.id, queue: 'report-generation' });
    }
    catch (err) {
        next(err);
    }
}
/**
 * POST /api/jobs/notification
 * Body: { recipientId, destination, body, jobType, subject?, socketEvent? }
 */
async function enqueueNotificationJob(req, res, next) {
    try {
        const { recipientId, destination, body, jobType = 'email', subject, socketEvent } = req.body;
        if (!recipientId || !destination || !body) {
            res.status(400).json({ success: false, message: 'recipientId, destination and body are required' });
            return;
        }
        const jobData = { jobType, recipientId, destination, body, subject, socketEvent };
        const job = await notification_queue_1.notificationQueue.add(jobType, jobData);
        res.status(202).json({ success: true, message: 'Notification job queued', jobId: job.id, queue: 'notification' });
    }
    catch (err) {
        next(err);
    }
}
// ── Status Endpoint ────────────────────────────────────────
/**
 * GET /api/jobs/:queue/:id
 * Returns the current state, progress and return value of a job.
 * Supports states: waiting, active, completed, failed, delayed, unknown.
 */
async function getJobStatus(req, res, next) {
    try {
        const { queue: queueName, id: jobId } = req.params;
        const queue = queueMap[queueName];
        if (!queue) {
            res.status(404).json({ success: false, message: `Queue '${queueName}' not found` });
            return;
        }
        const job = await queue.getJob(jobId);
        if (!job) {
            res.status(404).json({ success: false, message: `Job '${jobId}' not found` });
            return;
        }
        const state = await job.getState();
        const progress = job.progress;
        const result = job.returnvalue ?? null;
        const failReason = job.failedReason ?? null;
        res.json({
            success: true,
            job: {
                id: job.id,
                queue: queueName,
                state,
                progress,
                result,
                failReason,
                attemptsMade: job.attemptsMade,
                createdAt: new Date(job.timestamp).toISOString(),
            },
        });
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=job.controller.js.map