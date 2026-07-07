"use strict";
/**
 * complaint.repository.ts
 * Database queries for the Complaint collection.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.findAllComplaints = findAllComplaints;
exports.findComplaintById = findComplaintById;
exports.createComplaint = createComplaint;
exports.updateComplaint = updateComplaint;
exports.deleteComplaint = deleteComplaint;
exports.countComplaintsByStatus = countComplaintsByStatus;
const Complaint_1 = require("../models/Complaint");
async function findAllComplaints(pagination, filter = {}) {
    const [complaints, total] = await Promise.all([
        Complaint_1.Complaint.find(filter)
            .populate('cameraId', 'name location')
            .populate('assignedTo', 'name email')
            .populate('createdBy', 'name email')
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ createdAt: -1 })
            .lean(),
        Complaint_1.Complaint.countDocuments(filter),
    ]);
    return { complaints: complaints, total };
}
async function findComplaintById(id) {
    return Complaint_1.Complaint.findById(id)
        .populate('cameraId', 'name location')
        .populate('assignedTo', 'name email')
        .populate('createdBy', 'name email')
        .lean();
}
async function createComplaint(data) {
    const complaint = new Complaint_1.Complaint(data);
    return complaint.save();
}
async function updateComplaint(id, data) {
    return Complaint_1.Complaint.findByIdAndUpdate(id, data, { new: true, runValidators: true }).lean();
}
async function deleteComplaint(id) {
    return Complaint_1.Complaint.findByIdAndDelete(id).lean();
}
async function countComplaintsByStatus() {
    return Complaint_1.Complaint.aggregate([
        { $group: { _id: '$status', count: { $sum: 1 } } },
    ]);
}
//# sourceMappingURL=complaint.repository.js.map