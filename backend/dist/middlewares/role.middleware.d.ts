/**
 * role.middleware.ts
 * Factory function that returns a middleware to check if the user
 * has one of the required roles. Always use AFTER authenticate middleware.
 *
 * Usage: router.get('/admin', authenticate, requireRole('admin'), handler)
 */
import { Response, NextFunction } from 'express';
import { AuthRequest, UserRole } from '../types';
export declare function requireRole(...roles: UserRole[]): (req: AuthRequest, res: Response, next: NextFunction) => void;
//# sourceMappingURL=role.middleware.d.ts.map