/**
 * response.ts
 * Helper functions to send consistent API responses.
 * Every endpoint uses these helpers so the response format never varies.
 */
import { Response } from 'express';
import { PaginationMeta } from '../types';
export declare function sendSuccess<T>(res: Response, message: string, data?: T, statusCode?: number): Response;
export declare function sendPaginated<T>(res: Response, message: string, data: T, pagination: PaginationMeta): Response;
export declare function sendError(res: Response, message: string, statusCode?: number): Response;
//# sourceMappingURL=response.d.ts.map