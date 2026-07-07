/**
 * pagination.ts
 * Parses page/limit from query params and builds MongoDB skip/limit values.
 * Also creates pagination metadata for the API response.
 */
import { Request } from 'express';
import { PaginationMeta } from '../types';
export interface PaginationOptions {
    page: number;
    limit: number;
    skip: number;
}
export declare function getPaginationOptions(req: Request): PaginationOptions;
export declare function buildPaginationMeta(total: number, page: number, limit: number): PaginationMeta;
//# sourceMappingURL=pagination.d.ts.map