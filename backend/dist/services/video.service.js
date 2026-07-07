"use strict";
/**
 * video.service.ts
 * Business logic for video upload and processing status.
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
exports.getAllVideos = getAllVideos;
exports.getVideoById = getVideoById;
exports.saveUploadedVideo = saveUploadedVideo;
exports.processVideo = processVideo;
exports.deleteVideo = deleteVideo;
const fs_1 = __importDefault(require("fs"));
const error_middleware_1 = require("../middlewares/error.middleware");
const videoRepo = __importStar(require("../repositories/video.repository"));
const mongoose_1 = require("mongoose");
async function getAllVideos(page, limit, status) {
    const filter = status ? { status } : {};
    return videoRepo.findAllVideos({ page, limit, skip: (page - 1) * limit }, filter);
}
async function getVideoById(id) {
    const video = await videoRepo.findVideoById(id);
    if (!video)
        throw new error_middleware_1.AppError('Video not found', 404);
    return video;
}
// Called after Multer saves the file to disk
async function saveUploadedVideo(file, userId, cameraId) {
    return videoRepo.createVideo({
        filename: file.filename,
        originalName: file.originalname,
        mimetype: file.mimetype,
        size: file.size,
        path: file.path,
        uploadedBy: userId,
        cameraId: cameraId ? new mongoose_1.Types.ObjectId(cameraId) : undefined,
        status: 'uploaded',
    });
}
// AI Integration Point: queues a video for processing
async function processVideo(videoId) {
    const video = await videoRepo.findVideoById(videoId);
    if (!video)
        throw new error_middleware_1.AppError('Video not found', 404);
    // Update status to queued
    await videoRepo.updateVideoStatus(videoId, 'queued');
    // TODO: Send request to Python AI service:
    // POST http://ai-service/api/videos/process
    // Body: { videoId, filePath: video.path }
    //
    // The AI service will call back via a webhook or update the DB directly
    // when it finishes, changing status to 'completed' or 'failed'.
    return { message: 'Video queued for processing', videoId };
}
async function deleteVideo(id) {
    const video = await videoRepo.findVideoById(id);
    if (!video)
        throw new error_middleware_1.AppError('Video not found', 404);
    // Delete the physical file from disk
    if (fs_1.default.existsSync(video.path)) {
        fs_1.default.unlinkSync(video.path);
    }
    return videoRepo.deleteVideo(id);
}
//# sourceMappingURL=video.service.js.map