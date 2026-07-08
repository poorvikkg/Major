"use strict";
/**
 * workers/index.ts
 * Central orchestrator for all BullMQ workers.
 * Call startWorkers() once at application startup and stopWorkers() on shutdown.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.startWorkers = startWorkers;
exports.stopWorkers = stopWorkers;
const video_worker_1 = require("./video.worker");
const complaint_worker_1 = require("./complaint.worker");
const report_worker_1 = require("./report.worker");
const notification_worker_1 = require("./notification.worker");
const logger_1 = require("../config/logger");
/** Holds references to all active workers so they can be stopped cleanly */
const activeWorkers = [];
/**
 * Initialise all four workers and register them for graceful shutdown.
 * Safe to call multiple times — subsequent calls are no-ops.
 */
function startWorkers() {
    if (activeWorkers.length > 0)
        return; // already started
    activeWorkers.push((0, video_worker_1.createVideoWorker)(), (0, complaint_worker_1.createComplaintWorker)(), (0, report_worker_1.createReportWorker)(), (0, notification_worker_1.createNotificationWorker)());
    logger_1.logger.info(`BullMQ: ${activeWorkers.length} workers started`);
}
/**
 * Gracefully close all workers.
 * Waits for in-progress jobs to finish before shutting down.
 */
async function stopWorkers() {
    logger_1.logger.info('BullMQ: stopping all workers...');
    await Promise.all(activeWorkers.map((w) => w.close()));
    activeWorkers.length = 0;
    logger_1.logger.info('BullMQ: all workers stopped');
}
//# sourceMappingURL=index.js.map