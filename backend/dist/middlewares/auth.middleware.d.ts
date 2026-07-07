/**
 * auth.middleware.ts
 * Checks that the request has a valid JWT token.
 * Attaches the user object to req.user for downstream handlers.
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function authenticate(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=auth.middleware.d.ts.map