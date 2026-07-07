"use strict";
/**
 * RecognitionLog.ts
 * Stores each face detection event from live cameras or uploaded videos.
 * Records who was detected, when, where, and with what confidence.
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
exports.RecognitionLog = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const RecognitionLogSchema = new mongoose_1.Schema({
    personName: { type: String, trim: true }, // undefined if unknown person
    isUnknown: { type: Boolean, default: false },
    confidence: {
        type: Number,
        required: true,
        min: 0,
        max: 1,
    },
    cameraId: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'Camera',
    },
    videoId: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'Video',
    },
    snapshot: { type: String }, // path to the captured face image
    timestamp: {
        type: Date,
        required: true,
        default: Date.now,
    },
}, { timestamps: true });
// Index for time-range queries and filtering by camera
RecognitionLogSchema.index({ timestamp: -1 });
RecognitionLogSchema.index({ cameraId: 1, timestamp: -1 });
RecognitionLogSchema.index({ isUnknown: 1 });
exports.RecognitionLog = mongoose_1.default.model('RecognitionLog', RecognitionLogSchema);
//# sourceMappingURL=RecognitionLog.js.map