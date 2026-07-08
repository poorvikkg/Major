"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.redisConnectionOptions = void 0;
const env_1 = require("./env");
const logger_1 = require("./logger");
/** Shared BullMQ connection config derived from environment variables */
exports.redisConnectionOptions = {
    host: env_1.env.redis.host,
    port: env_1.env.redis.port,
    ...(env_1.env.redis.password ? { password: env_1.env.redis.password } : {}),
    // Required by BullMQ — do not change these
    maxRetriesPerRequest: null,
    enableReadyCheck: false,
};
logger_1.logger.debug({ host: env_1.env.redis.host, port: env_1.env.redis.port }, 'Redis connection options loaded');
//# sourceMappingURL=redis.js.map