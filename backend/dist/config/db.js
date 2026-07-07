"use strict";
/**
 * db.ts
 * Connects to MongoDB using Mongoose.
 * Uses connection pooling (default: 5 connections).
 * Logs connection status and crashes on failure.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.connectDatabase = connectDatabase;
const mongoose_1 = __importDefault(require("mongoose"));
const env_1 = require("./env");
const logger_1 = require("./logger");
async function connectDatabase() {
    try {
        await mongoose_1.default.connect(env_1.env.mongoUri, {
            // Mongoose 8+ has sensible defaults, but let's be explicit
            maxPoolSize: 10, // max concurrent connections
        });
        logger_1.logger.info('✅ MongoDB connected successfully');
    }
    catch (error) {
        logger_1.logger.error({ error }, '❌ MongoDB connection failed');
        process.exit(1); // crash the app — cannot run without DB
    }
}
// Log when mongoose disconnects (e.g. during shutdown)
mongoose_1.default.connection.on('disconnected', () => {
    logger_1.logger.warn('⚠️ MongoDB disconnected');
});
//# sourceMappingURL=db.js.map