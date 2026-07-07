"use strict";
/**
 * Video.ts
 * Mongoose model for uploaded surveillance videos.
 * Tracks upload details and AI processing status.
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
exports.Video = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const VideoSchema = new mongoose_1.Schema({
    filename: {
        type: String,
        required: true,
    },
    originalName: {
        type: String,
        required: true,
    },
    mimetype: {
        type: String,
        required: true,
    },
    size: {
        type: Number,
        required: true,
    },
    duration: { type: Number }, // in seconds
    path: {
        type: String,
        required: true,
    },
    uploadedBy: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    cameraId: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'Camera',
    },
    status: {
        type: String,
        enum: ['uploaded', 'queued', 'processing', 'completed', 'failed'],
        default: 'uploaded',
    },
    // Will be populated by the AI service once processing is complete
    processingResult: { type: mongoose_1.Schema.Types.Mixed },
    errorMessage: { type: String },
}, { timestamps: true });
// Indexes for listing and filtering videos
VideoSchema.index({ uploadedBy: 1 });
VideoSchema.index({ status: 1 });
VideoSchema.index({ createdAt: -1 });
exports.Video = mongoose_1.default.model('Video', VideoSchema);
//# sourceMappingURL=Video.js.map