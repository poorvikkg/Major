/**
 * job.routes.ts
 * REST routes for enqueueing background jobs and checking their status.
 *
 * All enqueue endpoints return HTTP 202 Accepted — the request was received
 * but the actual work happens asynchronously in a worker.
 */
declare const router: import("express-serve-static-core").Router;
export default router;
//# sourceMappingURL=job.routes.d.ts.map