/**
 * video.controller.ts
 * Handles HTTP requests for video upload and management.
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function getAll(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getOne(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function upload(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function processVideo(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function remove(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
/**
 * POST /videos/analyse
 * One-shot: upload a video file and immediately queue it for face recognition.
 * Returns the video record with status=queued so the client can poll for results.
 */
export declare function analyseVideo(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=video.controller.d.ts.map