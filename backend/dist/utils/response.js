"use strict";
/**
 * response.ts
 * Helper functions to send consistent API responses.
 * Every endpoint uses these helpers so the response format never varies.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendSuccess = sendSuccess;
exports.sendPaginated = sendPaginated;
exports.sendError = sendError;
// Send a successful response
function sendSuccess(res, message, data, statusCode = 200) {
    const body = { success: true, message, data };
    return res.status(statusCode).json(body);
}
// Send a success response with pagination info
function sendPaginated(res, message, data, pagination) {
    const body = { success: true, message, data, pagination };
    return res.status(200).json(body);
}
// Send an error response
function sendError(res, message, statusCode = 400) {
    const body = { success: false, message };
    return res.status(statusCode).json(body);
}
//# sourceMappingURL=response.js.map