/**
 * complaint.worker.ts
 * Processes jobs from the complaint-ai queue.
 * Handles: speech-to-text, summarize-complaint, extract-information
 */

import { Worker, type Job } from 'bullmq';
import { redisConnectionOptions } from '../config/redis';
import { COMPLAINT_QUEUE_NAME } from '../queues/complaint.queue';
import { logger } from '../config/logger';
import type { ComplaintJobData, JobResult } from '../types/queue.types';

const CONCURRENCY = 3;

// ── Job Handlers ────────────────────────────────────────────

async function speechToText(job: Job<ComplaintJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Transcribing audio');

  await job.updateProgress(30);
  // e.g. const transcript = await speechService.transcribe(job.data.payload, job.data.language);

  await job.updateProgress(80);
  // e.g. await ComplaintRepository.saveTranscript(job.data.complaintId, transcript);

  await job.updateProgress(100);
  return { success: true, message: 'Audio transcribed successfully', data: { complaintId: job.data.complaintId } };
}

async function summarizeComplaint(job: Job<ComplaintJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Summarising complaint');

  await job.updateProgress(40);
  // e.g. const summary = await aiService.summarize(job.data.payload);

  await job.updateProgress(80);
  // e.g. await ComplaintRepository.saveSummary(job.data.complaintId, summary);

  await job.updateProgress(100);
  return { success: true, message: 'Complaint summarised', data: { complaintId: job.data.complaintId } };
}

async function extractInformation(job: Job<ComplaintJobData>): Promise<JobResult> {
  logger.info({ jobId: job.id, complaintId: job.data.complaintId }, 'Extracting information');

  await job.updateProgress(50);
  // e.g. const entities = await aiService.extract(job.data.payload);

  await job.updateProgress(80);
  // e.g. await ComplaintRepository.saveEntities(job.data.complaintId, entities);

  await job.updateProgress(100);
  return { success: true, message: 'Information extracted', data: { complaintId: job.data.complaintId } };
}

// ── Router ──────────────────────────────────────────────────

async function processJob(job: Job<ComplaintJobData>): Promise<JobResult> {
  switch (job.data.jobType) {
    case 'speech-to-text':
      return speechToText(job);
    case 'summarize-complaint':
      return summarizeComplaint(job);
    case 'extract-information':
      return extractInformation(job);
    default:
      throw new Error(`Unknown complaint job type: ${(job.data as ComplaintJobData).jobType}`);
  }
}

// ── Worker Instance ─────────────────────────────────────────

export function createComplaintWorker(): Worker<ComplaintJobData, JobResult> {
  const worker = new Worker<ComplaintJobData, JobResult>(
    COMPLAINT_QUEUE_NAME,
    processJob,
    {
      connection: redisConnectionOptions,
      concurrency: CONCURRENCY,
    },
  );

  worker.on('active', (job) => {
    logger.info({ jobId: job.id, jobType: job.data.jobType }, '[complaint-worker] Job started');
  });

  worker.on('completed', (job, result) => {
    logger.info({ jobId: job.id, result }, '[complaint-worker] Job completed');
  });

  worker.on('failed', (job, err) => {
    logger.error({ jobId: job?.id, err }, '[complaint-worker] Job failed');
  });

  worker.on('error', (err) => {
    logger.error({ err }, '[complaint-worker] Worker error');
  });

  return worker;
}
