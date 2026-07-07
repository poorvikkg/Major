"use strict";
/**
 * video.controller.ts
 * Handles HTTP requests for video upload and management.
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
exports.getAll = getAll;
exports.getOne = getOne;
exports.upload = upload;
exports.processVideo = processVideo;
exports.remove = remove;
const videoService = __importStar(require("../services/video.service"));
const response_1 = require("../utils/response");
const pagination_1 = require("../utils/pagination");
const error_middleware_1 = require("../middlewares/error.middleware");
async function getAll(req, res, next) {
    try {
        const { page, limit } = (0, pagination_1.getPaginationOptions)(req);
        const status = req.query.status;
        const { videos, total } = await videoService.getAllVideos(page, limit, status);
        (0, response_1.sendPaginated)(res, 'Videos retrieved', videos, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getOne(req, res, next) {
    try {
        const video = await videoService.getVideoById(req.params.id);
        (0, response_1.sendSuccess)(res, 'Video retrieved', video);
    }
    catch (err) {
        next(err);
    }
}
async function upload(req, res, next) {
    try {
        if (!req.file)
            throw new error_middleware_1.AppError('No video file uploaded', 400);
        const video = await videoService.saveUploadedVideo(req.file, req.user._id, req.body.cameraId);
        (0, response_1.sendSuccess)(res, 'Video uploaded successfully', video, 201);
    }
    catch (err) {
        next(err);
    }
}
async function processVideo(req, res, next) {
    try {
        const result = await videoService.processVideo(req.body.videoId);
        (0, response_1.sendSuccess)(res, 'Video queued for processing', result);
    }
    catch (err) {
        next(err);
    }
}
async function remove(req, res, next) {
    try {
        await videoService.deleteVideo(req.params.id);
        (0, response_1.sendSuccess)(res, 'Video deleted successfully');
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=video.controller.js.map