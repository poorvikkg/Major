/**
 * recognition.controller.ts
 * Handles HTTP requests for recognition logs and unknown faces.
 * Also exposes AI integration endpoints (stubs for now).
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function getLogs(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getUnknownFaces(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getAnalytics(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function recognize(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function registerFace(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=recognition.controller.d.ts.map