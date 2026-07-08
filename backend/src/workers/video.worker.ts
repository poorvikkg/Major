/**
 * video.worker.ts
 * Processes jobs from the video-processing queue.
 * Handles: process-video, analyze-cctv
 *
 * Each handler is a small focused function — easy to extend independently.
 */

import { Worker, type Job } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import { VIDEO_QUEUE_NAME } from '../queues/video.queue';
import { logger } from '../config/logger';
import type { VideoJobData, JobResult } from '../types/queue.types';

/** Concurrency: process 2 video jobs in parallel */
const CONCURRENCY = 2;

// ── Job Handlers ────────────────────────────────────────────

async function processVideo(job: Job<VideoJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, objectKey: job.data.objectKey }, 'Processing uploaded video');

  // Step 1 — validate input (25%)
  await job.updateProgress(25);
  if (!job.data.objectKey) {
    throw new Error('objectKey is required for video processing');
  }

  // Step 2 — placeholder: call your video processing service here (50%)
  await job.updateProgress(50);
  // e.g. await videoService.transcode(job.data.objectKey);

  // Step 3 — store result metadata (75%)
  await job.updateProgress(75);
  // e.g. await VideoRepository.updateStatus(job.data.videoId, 'processed');

  await job.updateProgress(100);
  return { success: true, message: 'Video processed successfully', data: { videoId: job.data.videoId } };
}

async function analyzeCctv(job: Job<VideoJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, cameraId: job.data.cameraId }, 'Analysing CCTV recording');

  await job.updateProgress(30);
  // e.g. await cctvAnalysisService.analyze(job.data.objectKey, job.data.cameraId);

  await job.updateProgress(80);
  // e.g. await CameraRepository.saveAnalysisResult(job.data.cameraId, results);

  await job.updateProgress(100);
  return { success: true, message: 'CCTV analysis complete', data: { cameraId: job.data.cameraId } };
}

// ── Router ──────────────────────────────────────────────────

async function processJob(job: Job<VideoJobData>): Promise<JobResult> {
  switch (job.data.jobType) {
    case 'process-video':
      return processVideo(job);
    case 'analyze-cctv':
      return analyzeCctv(job);
    default:
      throw new Error(`Unknown video job type: ${(job.data as VideoJobData).jobType}`);
  }
}

// ── Worker Instance ─────────────────────────────────────────

export function createVideoWorker(): Worker<VideoJobData, JobResult> {
  const worker = new Worker<VideoJobData, JobResult>(
    VIDEO_QUEUE_NAME,
    processJob,
    {
      connection: redisConnectionOptions,
      concurrency: CONCURRENCY,
    },
  );

  worker.on('active', (job) => {
    logger.info({ jobId: job.id, jobType: job.data.jobType }, '[video-worker] Job started');
  });

  worker.on('completed', (job, result) => {
    logger.info({ jobId: job.id, result }, '[video-worker] Job completed');
  });

  worker.on('failed', (job, err) => {
    logger.error({ jobId: job?.id, err }, '[video-worker] Job failed');
  });

  worker.on('error', (err) => {
    logger.error({ err }, '[video-worker] Worker error');
  });

  return worker;
}
