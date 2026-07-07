"use strict";
/**
 * upload.middleware.ts
 * Multer configuration for video file uploads.
 * Validates file type and size before saving to disk.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.uploadAttachment = exports.uploadVideo = void 0;
const multer_1 = __importDefault(require("multer"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const env_1 = require("../config/env");
// Ensure the upload directory exists at startup
const uploadDir = path_1.default.resolve(env_1.env.uploadDir);
if (!fs_1.default.existsSync(uploadDir)) {
    fs_1.default.mkdirSync(uploadDir, { recursive: true });
}
// Store files on disk with a timestamp-based filename to avoid conflicts
const storage = multer_1.default.diskStorage({
    destination: (_req, _file, cb) => {
        cb(null, uploadDir);
    },
    filename: (_req, file, cb) => {
        const timestamp = Date.now();
        const ext = path_1.default.extname(file.originalname);
        cb(null, `video_${timestamp}${ext}`);
    },
});
// Only allow video files
function fileFilter(_req, file, cb) {
    const allowedMimetypes = ['video/mp4', 'video/avi', 'video/mkv', 'video/mov', 'video/webm'];
    if (allowedMimetypes.includes(file.mimetype)) {
        cb(null, true);
    }
    else {
        cb(new Error('Only video files are allowed (mp4, avi, mkv, mov, webm)'));
    }
}
exports.uploadVideo = (0, multer_1.default)({
    storage,
    fileFilter,
    limits: { fileSize: 500 * 1024 * 1024 }, // 500 MB max
});
// For attachment uploads (complaint files)
const attachmentStorage = multer_1.default.diskStorage({
    destination: (_req, _file, cb) => {
        const dir = path_1.default.join(uploadDir, 'attachments');
        if (!fs_1.default.existsSync(dir))
            fs_1.default.mkdirSync(dir, { recursive: true });
        cb(null, dir);
    },
    filename: (_req, file, cb) => {
        const timestamp = Date.now();
        const ext = path_1.default.extname(file.originalname);
        cb(null, `attachment_${timestamp}${ext}`);
    },
});
exports.uploadAttachment = (0, multer_1.default)({
    storage: attachmentStorage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB max
});
//# sourceMappingURL=upload.middleware.js.map