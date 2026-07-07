/**
 * error.middleware.ts
 * Central error handling middleware.
 * All unhandled errors bubble up here. We format them into a clean JSON response.
 * This prevents stack traces from leaking to the client in production.
 */
import { Request, Response, NextFunction } from 'express';
export declare class AppError extends Error {
    message: string;
    statusCode: number;
    constructor(message: string, statusCode?: number);
}
export declare function errorHandler(err: Error, req: Request, res: Response, _next: NextFunction): void;
//# sourceMappingURL=error.middleware.d.ts.map