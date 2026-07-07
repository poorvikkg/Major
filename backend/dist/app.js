"use strict";
/**
 * app.ts
 * Express application setup.
 * Configures middleware stack (security, logging, parsing, routes, error handling).
 * Kept separate from server.ts so it can be imported for testing.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const path_1 = __importDefault(require("path"));
const env_1 = require("./config/env");
const routes_1 = __importDefault(require("./routes"));
const error_middleware_1 = require("./middlewares/error.middleware");
const app = (0, express_1.default)();
// ── Security ────────────────────────────────────────────
// Helmet sets security HTTP headers (XSS protection, HSTS, etc.)
app.use((0, helmet_1.default)({ crossOriginResourcePolicy: { policy: 'cross-origin' } }));
// CORS: allow requests only from the frontend URL
app.use((0, cors_1.default)({ origin: env_1.env.corsOrigin, credentials: true }));
// Rate limiting: prevents brute-force and DDoS attacks
const limiter = (0, express_rate_limit_1.default)({
    windowMs: env_1.env.rateLimitWindowMs, // 15 minutes
    max: env_1.env.rateLimitMax, // 100 requests per window
    message: { success: false, message: 'Too many requests, please try again later' },
});
app.use('/api/', limiter);
// ── Performance ──────────────────────────────────────────
// Compress response bodies to reduce bandwidth
app.use((0, compression_1.default)());
// ── Parsing ──────────────────────────────────────────────
app.use(express_1.default.json({ limit: '10mb' }));
app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
// ── Static Files ─────────────────────────────────────────
// Serve uploaded files (videos, snapshots) as static assets
app.use('/uploads', express_1.default.static(path_1.default.resolve(env_1.env.uploadDir)));
// ── Routes ───────────────────────────────────────────────
app.use('/api', routes_1.default);
// Health check endpoint (useful for load balancers and monitoring)
app.get('/health', (_req, res) => {
    res.json({ success: true, message: 'Server is running', env: env_1.env.nodeEnv });
});
// 404 handler for unknown routes
app.use((_req, res) => {
    res.status(404).json({ success: false, message: 'Route not found' });
});
// ── Error Handler ─────────────────────────────────────────
// This MUST be the last middleware — catches all errors from above
app.use(error_middleware_1.errorHandler);
exports.default = app;
//# sourceMappingURL=app.js.map