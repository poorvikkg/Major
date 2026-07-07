"use strict";
/**
 * recognition.repository.ts
 * Database queries for RecognitionLog and UnknownFace collections.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.findAllLogs = findAllLogs;
exports.createLog = createLog;
exports.countTodayRecognitions = countTodayRecognitions;
exports.countUnknownDetections = countUnknownDetections;
exports.getDetectionsByDay = getDetectionsByDay;
exports.findAllUnknownFaces = findAllUnknownFaces;
exports.createUnknownFace = createUnknownFace;
const RecognitionLog_1 = require("../models/RecognitionLog");
const UnknownFace_1 = require("../models/UnknownFace");
// ── Recognition Logs ──────────────────────────────────
async function findAllLogs(pagination, filter = {}) {
    const [logs, total] = await Promise.all([
        RecognitionLog_1.RecognitionLog.find(filter)
            .populate('cameraId', 'name location')
            .populate('videoId', 'originalName')
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ timestamp: -1 })
            .lean(),
        RecognitionLog_1.RecognitionLog.countDocuments(filter),
    ]);
    return { logs: logs, total };
}
async function createLog(data) {
    return RecognitionLog_1.RecognitionLog.create(data);
}
// Count today's recognitions for dashboard stats
async function countTodayRecognitions() {
    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);
    return RecognitionLog_1.RecognitionLog.countDocuments({ timestamp: { $gte: startOfDay }, isUnknown: false });
}
async function countUnknownDetections() {
    return RecognitionLog_1.RecognitionLog.countDocuments({ isUnknown: true });
}
// Get recognitions per day (for analytics chart)
async function getDetectionsByDay(days = 7) {
    const since = new Date();
    since.setDate(since.getDate() - days);
    return RecognitionLog_1.RecognitionLog.aggregate([
        { $match: { timestamp: { $gte: since } } },
        {
            $group: {
                _id: { $dateToString: { format: '%Y-%m-%d', date: '$timestamp' } },
                count: { $sum: 1 },
                unknown: { $sum: { $cond: ['$isUnknown', 1, 0] } },
            },
        },
        { $sort: { _id: 1 } },
    ]);
}
// ── Unknown Faces ──────────────────────────────────────
async function findAllUnknownFaces(pagination) {
    const [faces, total] = await Promise.all([
        UnknownFace_1.UnknownFace.find()
            .populate('cameraId', 'name location')
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ timestamp: -1 })
            .lean(),
        UnknownFace_1.UnknownFace.countDocuments(),
    ]);
    return { faces: faces, total };
}
async function createUnknownFace(data) {
    return UnknownFace_1.UnknownFace.create(data);
}
//# sourceMappingURL=recognition.repository.js.map