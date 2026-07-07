"use strict";
/**
 * complaint.service.ts
 * Business logic for complaint creation and management.
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
exports.getAllComplaints = getAllComplaints;
exports.getComplaintById = getComplaintById;
exports.createComplaint = createComplaint;
exports.updateComplaint = updateComplaint;
exports.deleteComplaint = deleteComplaint;
exports.getComplaintStats = getComplaintStats;
const error_middleware_1 = require("../middlewares/error.middleware");
const complaintRepo = __importStar(require("../repositories/complaint.repository"));
const mongoose_1 = require("mongoose");
async function getAllComplaints(page, limit, status, priority) {
    const filter = {};
    if (status)
        filter.status = status;
    if (priority)
        filter.priority = priority;
    return complaintRepo.findAllComplaints({ page, limit, skip: (page - 1) * limit }, filter);
}
async function getComplaintById(id) {
    const complaint = await complaintRepo.findComplaintById(id);
    if (!complaint)
        throw new error_middleware_1.AppError('Complaint not found', 404);
    return complaint;
}
async function createComplaint(input, userId) {
    return complaintRepo.createComplaint({
        ...input,
        incidentAt: new Date(input.incidentAt),
        cameraId: input.cameraId ? new mongoose_1.Types.ObjectId(input.cameraId) : undefined,
        createdBy: userId,
    });
}
async function updateComplaint(id, input) {
    const complaint = await complaintRepo.updateComplaint(id, {
        ...input,
        assignedTo: input.assignedTo ? new mongoose_1.Types.ObjectId(input.assignedTo) : undefined,
    });
    if (!complaint)
        throw new error_middleware_1.AppError('Complaint not found', 404);
    return complaint;
}
async function deleteComplaint(id) {
    const complaint = await complaintRepo.deleteComplaint(id);
    if (!complaint)
        throw new error_middleware_1.AppError('Complaint not found', 404);
    return complaint;
}
async function getComplaintStats() {
    const stats = await complaintRepo.countComplaintsByStatus();
    return stats.reduce((acc, { _id, count }) => ({ ...acc, [_id]: count }), {});
}
//# sourceMappingURL=complaint.service.js.map