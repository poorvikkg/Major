"use strict";
/**
 * db.ts
 * Connects to MongoDB using Mongoose.
 * Uses connection pooling (default: 5 connections).
 * Logs connection status and crashes on failure.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
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
        // Seed default admin user if not present
        const { User } = await Promise.resolve().then(() => __importStar(require('../models/User')));
        const adminExists = await User.findOne({ email: 'admin@123' });
        if (!adminExists) {
            await User.create({
                name: 'Administrator',
                email: 'admin@123',
                password: 'admin123',
                role: 'admin',
                isActive: true,
            });
            logger_1.logger.info('👤 Seeded default admin account: admin@123 / admin123');
        }
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