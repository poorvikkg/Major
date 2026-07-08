"use strict";
/**
 * job.routes.ts
 * REST routes for enqueueing background jobs and checking their status.
 *
 * All enqueue endpoints return HTTP 202 Accepted — the request was received
 * but the actual work happens asynchronously in a worker.
 */
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const job_controller_1 = require("../controllers/job.controller");
const router = (0, express_1.Router)();
// ── Enqueue ─────────────────────────────────────────────────
router.post('/video', job_controller_1.enqueueVideoJob);
router.post('/complaint', job_controller_1.enqueueComplaintJob);
router.post('/report', job_controller_1.enqueueReportJob);
router.post('/notification', job_controller_1.enqueueNotificationJob);
// ── Status ──────────────────────────────────────────────────
// GET /api/jobs/:queue/:id  →  { id, state, progress, result, failReason }
router.get('/:queue/:id', job_controller_1.getJobStatus);
exports.default = router;
//# sourceMappingURL=job.routes.js.map