/**
 * queue.types.ts
 * Strict TypeScript interfaces for all BullMQ job payloads and results.
 * Import these in both queues and workers to keep types in sync.
 */
/** Job types handled by the video-processing queue */
export type VideoJobType = 'process-video' | 'analyze-cctv';
export interface VideoJobData {
    jobType: VideoJobType;
    videoId: string;
    /** S3/MinIO object key of the uploaded file */
    objectKey: string;
    cameraId?: string;
    requestedBy: string;
}
/** Job types handled by the complaint-ai queue */
export type ComplaintJobType = 'speech-to-text' | 'summarize-complaint' | 'extract-information';
export interface ComplaintJobData {
    jobType: ComplaintJobType;
    complaintId: string;
    /** Raw text or audio S3 key depending on jobType */
    payload: string;
    language?: string;
}
/** Job types handled by the report-generation queue */
export type ReportJobType = 'generate-pdf' | 'daily-report' | 'weekly-report';
export interface ReportJobData {
    jobType: ReportJobType;
    reportId: string;
    /** ISO date string: report covers this date (or week starting this date) */
    targetDate: string;
    requestedBy: string;
}
/** Job types handled by the notification queue */
export type NotificationJobType = 'email' | 'sms' | 'push' | 'socket';
export interface NotificationJobData {
    jobType: NotificationJobType;
    recipientId: string;
    /** Channel-specific address: email address, phone number, device token, etc. */
    destination: string;
    subject?: string;
    body: string;
    /** Socket.IO event name (only used when jobType === 'socket') */
    socketEvent?: string;
}
/** Standard shape returned by every worker on success */
export interface JobResult {
    success: boolean;
    message: string;
    /** Any domain-specific data the worker wants to surface */
    data?: Record<string, unknown>;
}
//# sourceMappingURL=queue.types.d.ts.map