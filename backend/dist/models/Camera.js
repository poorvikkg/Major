"use strict";
/**
 * Camera.ts
 * Mongoose model for surveillance cameras.
 * Supports IP cameras, RTSP streams, USB cameras, and cloud cameras.
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
exports.Camera = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const CameraSchema = new mongoose_1.Schema({
    name: {
        type: String,
        required: [true, 'Camera name is required'],
        trim: true,
        maxlength: 100,
    },
    location: {
        type: String,
        required: [true, 'Camera location is required'],
        trim: true,
    },
    rtspUrl: {
        type: String,
        trim: true,
    },
    ipAddress: {
        type: String,
        trim: true,
    },
    type: {
        type: String,
        enum: ['ip', 'rtsp', 'usb', 'cloud'],
        required: true,
    },
    status: {
        type: String,
        enum: ['online', 'offline', 'maintenance'],
        default: 'offline',
    },
    isActive: { type: Boolean, default: true },
    lastActive: { type: Date },
    addedBy: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
}, { timestamps: true });
// Indexes for common queries
CameraSchema.index({ status: 1 });
CameraSchema.index({ isActive: 1 });
CameraSchema.index({ addedBy: 1 });
exports.Camera = mongoose_1.default.model('Camera', CameraSchema);
//# sourceMappingURL=Camera.js.map