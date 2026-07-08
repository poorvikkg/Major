"use strict";
/**
 * report.worker.ts
 * Processes jobs from the report-generation queue.
 * Handles: generate-pdf, daily-report, weekly-report
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createReportWorker = createReportWorker;
const bullmq_1 = require("bullmq");
const redis_1 = require("../config/redis");
const report_queue_1 = require("../queues/report.queue");
const logger_1 = require("../config/logger");
const CONCURRENCY = 2;
// ── Job Handlers ────────────────────────────────────────────
async function generatePdf(job) {
    logger_1.logger.info({ jobId: job.id, reportId: job.data.reportId }, 'Generating PDF report');
    await job.updateProgress(20);
    // e.g. const data = await ReportRepository.fetchData(job.data.reportId);
    await job.updateProgress(60);
    // e.g. const pdfBuffer = await pdfService.render(data);
    await job.updateProgress(90);
    // e.g. const objectKey = await minioService.upload(pdfBuffer, `reports/${job.data.reportId}.pdf`);
    await job.updateProgress(100);
    return { success: true, message: 'PDF generated', data: { reportId: job.data.reportId } };
}
async function dailyReport(job) {
    logger_1.logger.info({ jobId: job.id, targetDate: job.data.targetDate }, 'Generating daily report');
    await job.updateProgress(25);
    // e.g. const stats = await statsService.getDailyStats(job.data.targetDate);
    await job.updateProgress(75);
    // e.g. await generatePdfFromStats(stats, job.data.reportId);
    await job.updateProgress(100);
    return { success: true, message: 'Daily report generated', data: { targetDate: job.data.targetDate } };
}
async function weeklyReport(job) {
    logger_1.logger.info({ jobId: job.id, targetDate: job.data.targetDate }, 'Generating weekly report');
    await job.updateProgress(25);
    // e.g. const stats = await statsService.getWeeklyStats(job.data.targetDate);
    await job.updateProgress(75);
    // e.g. await generatePdfFromStats(stats, job.data.reportId);
    await job.updateProgress(100);
    return { success: true, message: 'Weekly report generated', data: { targetDate: job.data.targetDate } };
}
// ── Router ──────────────────────────────────────────────────
async function processJob(job) {
    switch (job.data.jobType) {
        case 'generate-pdf':
            return generatePdf(job);
        case 'daily-report':
            return dailyReport(job);
        case 'weekly-report':
            return weeklyReport(job);
        default:
            throw new Error(`Unknown report job type: ${job.data.jobType}`);
    }
}
// ── Worker Instance ─────────────────────────────────────────
function createReportWorker() {
    const worker = new bullmq_1.Worker(report_queue_1.REPORT_QUEUE_NAME, processJob, {
        connection: redis_1.redisConnectionOptions,
        concurrency: CONCURRENCY,
    });
    worker.on('active', (job) => {
        logger_1.logger.info({ jobId: job.id, jobType: job.data.jobType }, '[report-worker] Job started');
    });
    worker.on('completed', (job, result) => {
        logger_1.logger.info({ jobId: job.id, result }, '[report-worker] Job completed');
    });
    worker.on('failed', (job, err) => {
        logger_1.logger.error({ jobId: job?.id, err }, '[report-worker] Job failed');
    });
    worker.on('error', (err) => {
        logger_1.logger.error({ err }, '[report-worker] Worker error');
    });
    return worker;
}
//# sourceMappingURL=report.worker.js.map