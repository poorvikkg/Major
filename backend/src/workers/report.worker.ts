/**
 * report.worker.ts
 * Processes jobs from the report-generation queue.
 * Handles: generate-pdf, daily-report, weekly-report
 */

import { Worker, type Job } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import { REPORT_QUEUE_NAME } from '../queues/report.queue';
import { logger } from '../config/logger';
import type { ReportJobData, JobResult } from '../types/queue.types';

const CONCURRENCY = 2;

// ── Job Handlers ────────────────────────────────────────────

async function generatePdf(job: Job<ReportJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, reportId: job.data.reportId }, 'Generating PDF report');

  await job.updateProgress(20);
  // e.g. const data = await ReportRepository.fetchData(job.data.reportId);

  await job.updateProgress(60);
  // e.g. const pdfBuffer = await pdfService.render(data);

  await job.updateProgress(90);
  // e.g. const objectKey = await minioService.upload(pdfBuffer, `reports/${job.data.reportId}.pdf`);

  await job.updateProgress(100);
  return { success: true, message: 'PDF generated', data: { reportId: job.data.reportId } };
}

async function dailyReport(job: Job<ReportJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, targetDate: job.data.targetDate }, 'Generating daily report');

  await job.updateProgress(25);
  // e.g. const stats = await statsService.getDailyStats(job.data.targetDate);

  await job.updateProgress(75);
  // e.g. await generatePdfFromStats(stats, job.data.reportId);

  await job.updateProgress(100);
  return { success: true, message: 'Daily report generated', data: { targetDate: job.data.targetDate } };
}

async function weeklyReport(job: Job<ReportJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, targetDate: job.data.targetDate }, 'Generating weekly report');

  await job.updateProgress(25);
  // e.g. const stats = await statsService.getWeeklyStats(job.data.targetDate);

  await job.updateProgress(75);
  // e.g. await generatePdfFromStats(stats, job.data.reportId);

  await job.updateProgress(100);
  return { success: true, message: 'Weekly report generated', data: { targetDate: job.data.targetDate } };
}

// ── Router ──────────────────────────────────────────────────

async function processJob(job: Job<ReportJobData>): Promise<JobResult> {
  switch (job.data.jobType) {
    case 'generate-pdf':
      return generatePdf(job);
    case 'daily-report':
      return dailyReport(job);
    case 'weekly-report':
      return weeklyReport(job);
    default:
      throw new Error(`Unknown report job type: ${(job.data as ReportJobData).jobType}`);
  }
}

// ── Worker Instance ─────────────────────────────────────────

export function createReportWorker(): Worker<ReportJobData, JobResult> {
  const worker = new Worker<ReportJobData, JobResult>(
    REPORT_QUEUE_NAME,
    processJob,
    {
      connection: redisConnectionOptions,
      concurrency: CONCURRENCY,
    },
  );

  worker.on('active', (job) => {
    logger.info({ jobId: job.id, jobType: job.data.jobType }, '[report-worker] Job started');
  });

  worker.on('completed', (job, result) => {
    logger.info({ jobId: job.id, result }, '[report-worker] Job completed');
  });

  worker.on('failed', (job, err) => {
    logger.error({ jobId: job?.id, err }, '[report-worker] Job failed');
  });

  worker.on('error', (err) => {
    logger.error({ err }, '[report-worker] Worker error');
  });

  return worker;
}
