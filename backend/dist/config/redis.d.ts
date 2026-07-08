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
/** Shared BullMQ connection config derived from environment variables */
export declare const redisConnectionOptions: ConnectionOptions;
//# sourceMappingURL=redis.d.ts.map