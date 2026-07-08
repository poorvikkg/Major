/**
 * complaint.worker.ts
 * Processes jobs from the complaint-ai queue.
 * Handles: speech-to-text, summarize-complaint, extract-information
 */
import { Worker } from 'bullmq';
import type { ComplaintJobData, JobResult } from '../types/queue.types';
export declare function createComplaintWorker(): Worker<ComplaintJobData, JobResult>;
//# sourceMappingURL=complaint.worker.d.ts.map