/**
 * job.routes.ts
 * REST routes for enqueueing background jobs and checking their status.
 *
 * All enqueue endpoints return HTTP 202 Accepted — the request was received
 * but the actual work happens asynchronously in a worker.
 */

import { Router } from 'express';
import {
  enqueueVideoJob,
  enqueueComplaintJob,
  enqueueReportJob,
  enqueueNotificationJob,
  getJobStatus,
} from '../controllers/job.controller';

const router = Router();

// ── Enqueue ─────────────────────────────────────────────────
router.post('/video', enqueueVideoJob);
router.post('/complaint', enqueueComplaintJob);
router.post('/report', enqueueReportJob);
router.post('/notification', enqueueNotificationJob);

// ── Status ──────────────────────────────────────────────────
// GET /api/jobs/:queue/:id  →  { id, state, progress, result, failReason }
router.get('/:queue/:id', getJobStatus);

export default router;
