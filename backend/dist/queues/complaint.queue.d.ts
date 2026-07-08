/**
 * complaint.queue.ts
 * BullMQ queue for AI complaint processing jobs (speech-to-text, summarisation, extraction).
 */
import { Queue } from 'bullmq';
import type { ComplaintJobData } from '../types/queue.types';
export declare const COMPLAINT_QUEUE_NAME = "complaint-ai";
export declare const complaintQueue: Queue<ComplaintJobData, any, string, ComplaintJobData, any, string>;
//# sourceMappingURL=complaint.queue.d.ts.map