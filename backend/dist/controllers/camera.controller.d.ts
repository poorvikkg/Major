/**
 * camera.controller.ts
 * Handles HTTP requests for camera management endpoints.
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function getAll(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getOne(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function create(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function update(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function remove(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function startCamera(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function stopCamera(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=camera.controller.d.ts.map