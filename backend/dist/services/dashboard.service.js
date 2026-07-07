"use strict";
/**
 * dashboard.service.ts
 * Aggregates data from multiple collections for the dashboard overview.
 * Runs queries in parallel using Promise.all for better performance.
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDashboardStats = getDashboardStats;
exports.getRecentAlerts = getRecentAlerts;
exports.getRecentComplaints = getRecentComplaints;
exports.getRecentActivity = getRecentActivity;
const userRepo = __importStar(require("../repositories/user.repository"));
const cameraRepo = __importStar(require("../repositories/camera.repository"));
const videoRepo = __importStar(require("../repositories/video.repository"));
const recognitionRepo = __importStar(require("../repositories/recognition.repository"));
const RecognitionLog_1 = require("../models/RecognitionLog");
const Complaint_1 = require("../models/Complaint");
const SystemLog_1 = require("../models/SystemLog");
async function getDashboardStats() {
    // Run all counts in parallel — much faster than sequential queries
    const [userCount, cameraStats, videosProcessed, todayRecognitions, unknownDetections] = await Promise.all([
        userRepo.countUsers(),
        cameraRepo.getCameraStats(),
        videoRepo.countVideos(),
        recognitionRepo.countTodayRecognitions(),
        recognitionRepo.countUnknownDetections(),
    ]);
    return {
        users: { total: userCount },
        cameras: cameraStats,
        videos: { processed: videosProcessed },
        recognitions: {
            today: todayRecognitions,
            unknownDetections,
        },
    };
}
// Get recent alerts (unknown faces detected in last 24h)
async function getRecentAlerts(limit = 5) {
    const since = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return RecognitionLog_1.RecognitionLog.find({ isUnknown: true, timestamp: { $gte: since } })
        .populate('cameraId', 'name location')
        .sort({ timestamp: -1 })
        .limit(limit)
        .lean();
}
// Get recent complaints
async function getRecentComplaints(limit = 5) {
    return Complaint_1.Complaint.find()
        .sort({ createdAt: -1 })
        .limit(limit)
        .lean();
}
// Get recent system activity
async function getRecentActivity(limit = 10) {
    return SystemLog_1.SystemLog.find()
        .populate('userId', 'name')
        .sort({ createdAt: -1 })
        .limit(limit)
        .lean();
}
//# sourceMappingURL=dashboard.service.js.map