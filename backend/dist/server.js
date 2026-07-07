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
const env_1 = require("./config/env");
const logger_1 = require("./config/logger");
async function startServer() {
    // 1. Connect to MongoDB first — fail fast if DB is unavailable
    await (0, db_1.connectDatabase)();
    // 2. Create the HTTP server wrapping Express
    const httpServer = http_1.default.createServer(app_1.default);
    // 3. Attach Socket.IO to the same HTTP server
    (0, socket_1.initializeSocket)(httpServer);
    // 4. Start listening
    httpServer.listen(env_1.env.port, () => {
        logger_1.logger.info(`🚀 Server running on http://localhost:${env_1.env.port}`);
        logger_1.logger.info(`📁 Environment: ${env_1.env.nodeEnv}`);
        logger_1.logger.info(`🔌 Socket.IO ready`);
    });
    // 5. Handle graceful shutdown (e.g. Ctrl+C or process kill)
    process.on('SIGTERM', () => {
        logger_1.logger.info('SIGTERM received. Shutting down gracefully...');
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