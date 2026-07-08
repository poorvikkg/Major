/**
 * video.queue.ts
 * BullMQ queue for video processing jobs (uploads, CCTV analysis).
 * Controllers call videoQueue.add() to enqueue work without blocking the request.
 */
import { Queue } from 'bullmq';
import type { VideoJobData } from '../types/queue.types';
export declare const VIDEO_QUEUE_NAME = "video-processing";
export declare const videoQueue: Queue<VideoJobData, any, string, VideoJobData, any, string>;
//# sourceMappingURL=video.queue.d.ts.map