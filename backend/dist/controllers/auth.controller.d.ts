/**
 * auth.controller.ts
 * Handles HTTP requests for authentication endpoints.
 * Delegates business logic to auth.service.ts.
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function register(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function login(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getMe(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function logout(_req: AuthRequest, res: Response): void;
//# sourceMappingURL=auth.controller.d.ts.map