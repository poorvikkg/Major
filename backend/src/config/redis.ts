/**
 * redis.ts
 * Provides the single Redis connection configuration for BullMQ.
 *
 * BullMQ accepts a plain ConnectionOptions object (host/port/password)
 * and internally creates its own IORedis connections — one per Queue,
 * one per Worker. This avoids the "two ioredis" type conflict that
 * occurs when you pass an external IORedis instance.
 *
 * Every queue and worker imports `redisConnectionOptions` from here.
 */

import type { ConnectionOptions } from 'bullmq';
import { env } from './env';
import { logger } from './logger';

/** Shared BullMQ connection config derived from environment variables */
export const redisConnectionOptions: ConnectionOptions = {
  host: env.redis.host,
  port: env.redis.port,
  ...(env.redis.password ? { password: env.redis.password } : {}),
  // Required by BullMQ — do not change these
  maxRetriesPerRequest: null,
  enableReadyCheck: false,
};

logger.debug(
  { host: env.redis.host, port: env.redis.port },
  'Redis connection options loaded',
);
