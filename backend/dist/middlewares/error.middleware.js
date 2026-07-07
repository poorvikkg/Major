"use strict";
/**
 * error.middleware.ts
 * Central error handling middleware.
 * All unhandled errors bubble up here. We format them into a clean JSON response.
 * This prevents stack traces from leaking to the client in production.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppError = void 0;
exports.errorHandler = errorHandler;
const logger_1 = require("../config/logger");
const env_1 = require("../config/env");
// Custom error class with an HTTP status code
class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.message = message;
        this.statusCode = statusCode;
        this.name = 'AppError';
    }
}
exports.AppError = AppError;
// Global error handler — must have 4 parameters for Express to recognize it
function errorHandler(err, req, res, 
// eslint-disable-next-line @typescript-eslint/no-unused-vars
_next) {
    logger_1.logger.error({ err, url: req.url, method: req.method }, 'Unhandled error');
    // Handle known operational errors (thrown via AppError)
    if (err instanceof AppError) {
        res.status(err.statusCode).json({ success: false, message: err.message });
        return;
    }
    // Handle Mongoose validation errors
    if (err.name === 'ValidationError') {
        res.status(422).json({ success: false, message: err.message });
        return;
    }
    // Handle duplicate key errors (e.g. duplicate email)
    if (err.code === 11000) {
        const field = Object.keys(err.keyValue || {})[0];
        res.status(409).json({ success: false, message: `${field} already exists` });
        return;
    }
    // Generic server error — hide details in production
    res.status(500).json({
        success: false,
        message: 'Internal server error',
        ...(env_1.env.isDev && { stack: err.stack }), // show stack trace only in dev
    });
}
//# sourceMappingURL=error.middleware.js.map