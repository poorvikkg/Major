"use strict";
/**
 * SystemLog.ts
 * Audit trail for important system events (logins, config changes, etc.).
 * Helps admins track what happened and who did it.
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
exports.SystemLog = void 0;
const mongoose_1 = __importStar(require("mongoose"));
const SystemLogSchema = new mongoose_1.Schema({
    userId: {
        type: mongoose_1.Schema.Types.ObjectId,
        ref: 'User',
    },
    action: {
        type: String,
        required: true,
        // e.g. 'LOGIN', 'CREATE_CAMERA', 'DELETE_USER'
    },
    resource: {
        type: String,
        required: true,
        // e.g. 'User', 'Camera', 'Video'
    },
    resourceId: { type: String },
    details: { type: mongoose_1.Schema.Types.Mixed },
    ipAddress: { type: String },
    userAgent: { type: String },
}, {
    timestamps: { createdAt: true, updatedAt: false }, // we only need createdAt for logs
});
SystemLogSchema.index({ userId: 1 });
SystemLogSchema.index({ action: 1 });
SystemLogSchema.index({ createdAt: -1 });
exports.SystemLog = mongoose_1.default.model('SystemLog', SystemLogSchema);
//# sourceMappingURL=SystemLog.js.map