"use strict";
/**
 * recognition.service.ts
 * Business logic for recognition logs and unknown face alerts.
 * Also contains AI integration points for the future Python service.
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
exports.getLogs = getLogs;
exports.getUnknownFaces = getUnknownFaces;
exports.getDetectionsByDay = getDetectionsByDay;
exports.logRecognition = logRecognition;
exports.registerFace = registerFace;
exports.recognize = recognize;
const mongoose_1 = require("mongoose");
const recognitionRepo = __importStar(require("../repositories/recognition.repository"));
async function getLogs(page, limit, cameraId) {
    const filter = cameraId ? { cameraId } : {};
    return recognitionRepo.findAllLogs({ page, limit, skip: (page - 1) * limit }, filter);
}
async function getUnknownFaces(page, limit) {
    return recognitionRepo.findAllUnknownFaces({ page, limit, skip: (page - 1) * limit });
}
async function getDetectionsByDay(days) {
    return recognitionRepo.getDetectionsByDay(days);
}
// AI Integration Point: will be called by Python AI service via webhook
// to log a new face recognition event
async function logRecognition(data) {
    return recognitionRepo.createLog({
        personName: data.personName,
        isUnknown: data.isUnknown,
        confidence: data.confidence,
        cameraId: data.cameraId ? new mongoose_1.Types.ObjectId(data.cameraId) : undefined,
        videoId: data.videoId ? new mongoose_1.Types.ObjectId(data.videoId) : undefined,
        snapshot: data.snapshot,
        timestamp: data.timestamp || new Date(),
    });
}
// AI Integration Point: registers a new face in the AI database
async function registerFace(_data) {
    // TODO: POST to Python AI service: http://ai-service/api/register-face
    return { message: 'Face registration queued for AI processing' };
}
// AI Integration Point: run recognition on a single image
async function recognize(_imageBase64) {
    // TODO: POST to Python AI service: http://ai-service/api/recognize
    return { message: 'Recognition request sent to AI service' };
}
//# sourceMappingURL=recognition.service.js.map