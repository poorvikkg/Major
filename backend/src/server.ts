/**
 * server.ts
 * Entry point: creates the HTTP server, initializes Socket.IO,
 * connects to MongoDB, and starts listening for requests.
 */

import http from 'http';
import app from './app';
import { connectDatabase } from './config/db';
import { initializeSocket } from './socket/socket';
import { initializeMinio } from './services/minio.service';
import { env } from './config/env';
import { logger } from './config/logger';

async function startServer(): Promise<void> {
  // 1. Connect to MongoDB first — fail fast if DB is unavailable
  await connectDatabase();

  // 2. Initialize S3 Object Storage (MinIO)
  await initializeMinio().catch((err) => {
    logger.error('Failed to initialize MinIO bucket:', err);
  });

  // 2. Create the HTTP server wrapping Express
  const httpServer = http.createServer(app);

  // 3. Attach Socket.IO to the same HTTP server
  initializeSocket(httpServer);

  // 4. Start listening
  httpServer.listen(env.port, () => {
    logger.info(`🚀 Server running on http://localhost:${env.port}`);
    logger.info(`📁 Environment: ${env.nodeEnv}`);
    logger.info(`🔌 Socket.IO ready`);
  });

  // 5. Handle graceful shutdown (e.g. Ctrl+C or process kill)
  process.on('SIGTERM', () => {
    logger.info('SIGTERM received. Shutting down gracefully...');
    httpServer.close(() => {
      logger.info('HTTP server closed');
      process.exit(0);
    });
  });
}

startServer().catch((err) => {
  logger.error({ err }, 'Failed to start server');
  process.exit(1);
});
