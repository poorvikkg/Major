"use strict";
/**
 * pagination.ts
 * Parses page/limit from query params and builds MongoDB skip/limit values.
 * Also creates pagination metadata for the API response.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPaginationOptions = getPaginationOptions;
exports.buildPaginationMeta = buildPaginationMeta;
// Extract and validate pagination params from query string
function getPaginationOptions(req) {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 10));
    const skip = (page - 1) * limit;
    return { page, limit, skip };
}
// Build the pagination metadata object for the response
function buildPaginationMeta(total, page, limit) {
    return {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
    };
}
//# sourceMappingURL=pagination.js.map