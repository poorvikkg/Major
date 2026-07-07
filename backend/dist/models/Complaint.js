"use strict";
/**
 * Complaint.ts
 * Stores user-submitted complaints about camera issues or incidents.
 * Supports priority, status tracking, and assignment to operators/admins.
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
exports.Complaint = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const ComplaintSchema = new mongoose_1.Schema({
    name: {
        type: String,
        required: [true, 'Name is required'],
        trim: true,
    },
    email: {
        type: String,
        required: [true, 'Email is required'],
        lowercase: true,
        trim: true,
    },
    phone: { type: String, trim: true },
    type: {
        type: String,
        enum: ['camera_issue', 'false_detection', 'system_error', 'unauthorized_access', 'other'],
        required: true,
    },
    cameraId: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'Camera',
    },
    incidentAt: {
        type: Date,
        required: [true, 'Incident date/time is required'],
    },
    description: {
        type: String,
        required: [true, 'Description is required'],
        maxlength: 2000,
    },
    attachment: { type: String }, // file path of uploaded attachment
    priority: {
        type: String,
        enum: ['low', 'medium', 'high', 'critical'],
        default: 'medium',
    },
    status: {
        type: String,
        enum: ['open', 'in_progress', 'resolved', 'closed'],
        default: 'open',
    },
    assignedTo: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'User',
    },
    remarks: { type: String, maxlength: 1000 },
    createdBy: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'User',
    },
}, { timestamps: true });
ComplaintSchema.index({ status: 1 });
ComplaintSchema.index({ priority: 1 });
ComplaintSchema.index({ createdAt: -1 });
ComplaintSchema.index({ assignedTo: 1 });
exports.Complaint = mongoose_1.default.model('Complaint', ComplaintSchema);
//# sourceMappingURL=Complaint.js.map