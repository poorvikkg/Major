/**
 * dashboard.controller.ts
 * Handles requests for dashboard data (stats, alerts, activity).
 */
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
export declare function getStats(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getRecentAlerts(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
export declare function getRecentActivity(req: AuthRequest, res: Response, next: NextFunction): Promise<void>;
//# sourceMappingURL=dashboard.controller.d.ts.map