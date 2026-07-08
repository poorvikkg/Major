/**
 * report.worker.ts
 * Processes jobs from the report-generation queue.
 * Handles: generate-pdf, daily-report, weekly-report
 */
import { Worker } from 'bullmq';
import type { ReportJobData, JobResult } from '../types/queue.types';
export declare function createReportWorker(): Worker<ReportJobData, JobResult>;
//# sourceMappingURL=report.worker.d.ts.map