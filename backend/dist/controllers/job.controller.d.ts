/**
 * job.controller.ts
 * Example controller showing the correct BullMQ pattern:
 *   Validate → Enqueue → Return 202 + Job ID
 *
 * Controllers never run long tasks; they delegate to workers via queues.
 */
import { type Request, type Response, type NextFunction } from 'express';
/**
 * POST /api/jobs/video
 * Body: { videoId, objectKey, requestedBy, jobType? }
 * Enqueues a video-processing job and returns 202 with the job ID.
 */
export declare function enqueueVideoJob(req: Request, res: Response, next: NextFunction): Promise<void>;
/**
 * POST /api/jobs/complaint
 * Body: { complaintId, payload, jobType, language? }
 */
export declare function enqueueComplaintJob(req: Request, res: Response, next: NextFunction): Promise<void>;
/**
 * POST /api/jobs/report
 * Body: { reportId, targetDate, requestedBy, jobType? }
 */
export declare function enqueueReportJob(req: Request, res: Response, next: NextFunction): Promise<void>;
/**
 * POST /api/jobs/notification
 * Body: { recipientId, destination, body, jobType, subject?, socketEvent? }
 */
export declare function enqueueNotificationJob(req: Request, res: Response, next: NextFunction): Promise<void>;
/**
 * GET /api/jobs/:queue/:id
 * Returns the current state, progress and return value of a job.
 * Supports states: waiting, active, completed, failed, delayed, unknown.
 */
export declare function getJobStatus(req: Request, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=job.controller.d.ts.map