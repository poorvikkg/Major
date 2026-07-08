/**
 * report.queue.ts
 * BullMQ queue for report generation jobs (PDF, daily, weekly).
 */
import { Queue } from 'bullmq';
import type { ReportJobData } from '../types/queue.types';
export declare const REPORT_QUEUE_NAME = "report-generation";
export declare const reportQueue: Queue<ReportJobData, any, string, ReportJobData, any, string>;
//# sourceMappingURL=report.queue.d.ts.map