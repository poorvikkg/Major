"use strict";
/**
 * server.ts
 * Entry point: creates the HTTP server, initializes Socket.IO,
 * connects to MongoDB, and starts listening for requests.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = __importDefault(require("http"));
const app_1 = __importDefault(require("./app"));
const db_1 = require("./config/db");
const socket_1 = require("./socket/socket");
const minio_service_1 = require("./services/minio.service");
const env_1 = require("./config/env");
const logger_1 = require("./config/logger");
const workers_1 = require("./workers");
async function startServer() {
    // 1. Connect to MongoDB first — fail fast if DB is unavailable
    await (0, db_1.connectDatabase)();
    // 2. Initialize S3 Object Storage (MinIO)
    await (0, minio_service_1.initializeMinio)().catch((err) => {
        logger_1.logger.error('Failed to initialize MinIO bucket:', err);
    });
    // 3. Create the HTTP server wrapping Express
    const httpServer = http_1.default.createServer(app_1.default);
    // 4. Attach Socket.IO to the same HTTP server
    (0, socket_1.initializeSocket)(httpServer);
    // 5. Start BullMQ workers (they connect to Redis independently)
    (0, workers_1.startWorkers)();
    // 6. Start listening
    httpServer.listen(env_1.env.port, () => {
        logger_1.logger.info(`Server running on http://localhost:${env_1.env.port}`);
        logger_1.logger.info(`Environment: ${env_1.env.nodeEnv}`);
    });
    // 7. Handle graceful shutdown — wait for in-flight jobs before exiting
    process.on('SIGTERM', async () => {
        logger_1.logger.info('SIGTERM received. Shutting down gracefully...');
        await (0, workers_1.stopWorkers)();
        httpServer.close(() => {
            logger_1.logger.info('HTTP server closed');
            process.exit(0);
        });
    });
}
startServer().catch((err) => {
    logger_1.logger.error({ err }, 'Failed to start server');
    process.exit(1);
});
//# sourceMappingURL=server.js.map