/**
 * job.controller.ts
 * Example controller showing the correct BullMQ pattern:
 *   Validate → Enqueue → Return 202 + Job ID
 *
 * Controllers never run long tasks; they delegate to workers via queues.
 */

import { type Request, type Response, type NextFunction } from 'express';
import { Queue } from 'bullmq';
import { videoQueue } from '../queues/video.queue';
import { complaintQueue } from '../queues/complaint.queue';
import { reportQueue } from '../queues/report.queue';
import { notificationQueue } from '../queues/notification.queue';
import type {
  VideoJobData,
  ComplaintJobData,
  ReportJobData,
  NotificationJobData,
} from '../types/queue.types';

// ── Queue name → Queue instance map for the status endpoint ──
const queueMap: Record<string, Queue> = {
  'video-processing': videoQueue,
  'complaint-ai': complaintQueue,
  'report-generation': reportQueue,
  notification: notificationQueue,
};

// ── Enqueue Handlers ────────────────────────────────────────

/**
 * POST /api/jobs/video
 * Body: { videoId, objectKey, requestedBy, jobType? }
 * Enqueues a video-processing job and returns 202 with the job ID.
 */
export async function enqueueVideoJob(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const { videoId, objectKey, requestedBy, jobType = 'process-video' } = req.body as Partial<VideoJobData>;

    if (!videoId || !objectKey || !requestedBy) {
      res.status(400).json({ success: false, message: 'videoId, objectKey and requestedBy are required' });
      return;
    }

    const jobData: VideoJobData = { jobType, videoId, objectKey, requestedBy };
    const job = await videoQueue.add(jobType, jobData);

    res.status(202).json({
      success: true,
      message: 'Video job queued',
      jobId: job.id,
      queue: 'video-processing',
    });
  } catch (err) {
    next(err);
  }
}

/**
 * POST /api/jobs/complaint
 * Body: { complaintId, payload, jobType, language? }
 */
export async function enqueueComplaintJob(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const { complaintId, payload, jobType = 'summarize-complaint', language } = req.body as Partial<ComplaintJobData>;

    if (!complaintId || !payload) {
      res.status(400).json({ success: false, message: 'complaintId and payload are required' });
      return;
    }

    const jobData: ComplaintJobData = { jobType, complaintId, payload, language };
    const job = await complaintQueue.add(jobType, jobData);

    res.status(202).json({ success: true, message: 'Complaint AI job queued', jobId: job.id, queue: 'complaint-ai' });
  } catch (err) {
    next(err);
  }
}

/**
 * POST /api/jobs/report
 * Body: { reportId, targetDate, requestedBy, jobType? }
 */
export async function enqueueReportJob(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const { reportId, targetDate, requestedBy, jobType = 'generate-pdf' } = req.body as Partial<ReportJobData>;

    if (!reportId || !targetDate || !requestedBy) {
      res.status(400).json({ success: false, message: 'reportId, targetDate and requestedBy are required' });
      return;
    }

    const jobData: ReportJobData = { jobType, reportId, targetDate, requestedBy };
    const job = await reportQueue.add(jobType, jobData);

    res.status(202).json({ success: true, message: 'Report job queued', jobId: job.id, queue: 'report-generation' });
  } catch (err) {
    next(err);
  }
}

/**
 * POST /api/jobs/notification
 * Body: { recipientId, destination, body, jobType, subject?, socketEvent? }
 */
export async function enqueueNotificationJob(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const { recipientId, destination, body, jobType = 'email', subject, socketEvent } = req.body as Partial<NotificationJobData>;

    if (!recipientId || !destination || !body) {
      res.status(400).json({ success: false, message: 'recipientId, destination and body are required' });
      return;
    }

    const jobData: NotificationJobData = { jobType, recipientId, destination, body, subject, socketEvent };
    const job = await notificationQueue.add(jobType, jobData);

    res.status(202).json({ success: true, message: 'Notification job queued', jobId: job.id, queue: 'notification' });
  } catch (err) {
    next(err);
  }
}

// ── Status Endpoint ────────────────────────────────────────

/**
 * GET /api/jobs/:queue/:id
 * Returns the current state, progress and return value of a job.
 * Supports states: waiting, active, completed, failed, delayed, unknown.
 */
export async function getJobStatus(
  req: Request,
  res: Response,
  next: NextFunction,
): Promise<void> {
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
  } catch (err) {
    next(err);
  }
}
