/**
 * video.worker.ts
 * Processes jobs from the video-processing queue.
 * Handles: process-video, analyze-cctv
 *
 * Each handler is a small focused function — easy to extend independently.
 */
import { Worker } from 'bullmq';
import type { VideoJobData, JobResult } from '../types/queue.types';
export declare function createVideoWorker(): Worker<VideoJobData, JobResult>;
//# sourceMappingURL=video.worker.d.ts.map