"use strict";
/**
 * complaint.controller.ts
 * Handles HTTP requests for complaint management.
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
exports.getAll = getAll;
exports.getOne = getOne;
exports.create = create;
exports.update = update;
exports.remove = remove;
exports.getStats = getStats;
const complaintService = __importStar(require("../services/complaint.service"));
const response_1 = require("../utils/response");
const pagination_1 = require("../utils/pagination");
const minio_service_1 = require("../services/minio.service");
const fs_1 = __importDefault(require("fs"));
async function getAll(req, res, next) {
    try {
        const { page, limit } = (0, pagination_1.getPaginationOptions)(req);
        const status = req.query.status;
        const priority = req.query.priority;
        // Viewers can only see their own complaints
        const createdBy = req.user?.role === 'viewer' ? req.user._id.toString() : undefined;
        const { complaints, total } = await complaintService.getAllComplaints(page, limit, status, priority, createdBy);
        (0, response_1.sendPaginated)(res, 'Complaints retrieved', complaints, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getOne(req, res, next) {
    try {
        const complaint = await complaintService.getComplaintById(req.params.id);
        (0, response_1.sendSuccess)(res, 'Complaint retrieved', complaint);
    }
    catch (err) {
        next(err);
    }
}
async function create(req, res, next) {
    try {
        const attachmentUrls = [];
        if (req.files && Array.isArray(req.files)) {
            const filesList = req.files;
            for (const file of filesList) {
                try {
                    const url = await (0, minio_service_1.uploadToMinio)(file.path, 'attachments');
                    attachmentUrls.push(url);
                }
                finally {
                    if (fs_1.default.existsSync(file.path))
                        fs_1.default.unlinkSync(file.path);
                }
            }
        }
        else if (req.file) {
            const file = req.file;
            try {
                const url = await (0, minio_service_1.uploadToMinio)(file.path, 'attachments');
                attachmentUrls.push(url);
            }
            finally {
                if (fs_1.default.existsSync(file.path))
                    fs_1.default.unlinkSync(file.path);
            }
        }
        req.body.attachments = attachmentUrls;
        const complaint = await complaintService.createComplaint(req.body, req.user?._id);
        (0, response_1.sendSuccess)(res, 'Complaint submitted successfully', complaint, 201);
    }
    catch (err) {
        next(err);
    }
}
async function update(req, res, next) {
    try {
        const complaint = await complaintService.updateComplaint(req.params.id, req.body);
        (0, response_1.sendSuccess)(res, 'Complaint updated', complaint);
    }
    catch (err) {
        next(err);
    }
}
async function remove(req, res, next) {
    try {
        await complaintService.deleteComplaint(req.params.id);
        (0, response_1.sendSuccess)(res, 'Complaint deleted');
    }
    catch (err) {
        next(err);
    }
}
async function getStats(req, res, next) {
    try {
        const stats = await complaintService.getComplaintStats();
        (0, response_1.sendSuccess)(res, 'Complaint stats retrieved', stats);
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=complaint.controller.js.map