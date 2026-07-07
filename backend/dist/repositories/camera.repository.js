"use strict";
/**
 * camera.repository.ts
 * Database queries for the Camera collection.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.findAllCameras = findAllCameras;
exports.findCameraById = findCameraById;
exports.createCamera = createCamera;
exports.updateCamera = updateCamera;
exports.deleteCamera = deleteCamera;
exports.getCameraStats = getCameraStats;
const Camera_1 = require("../models/Camera");
async function findAllCameras(pagination, filter = {}) {
    const [cameras, total] = await Promise.all([
        Camera_1.Camera.find(filter)
            .populate('addedBy', 'name email')
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ createdAt: -1 })
            .lean(),
        Camera_1.Camera.countDocuments(filter),
    ]);
    return { cameras: cameras, total };
}
async function findCameraById(id) {
    return Camera_1.Camera.findById(id).populate('addedBy', 'name email').lean();
}
async function createCamera(data) {
    const camera = new Camera_1.Camera(data);
    return camera.save();
}
async function updateCamera(id, data) {
    return Camera_1.Camera.findByIdAndUpdate(id, data, { new: true, runValidators: true }).lean();
}
async function deleteCamera(id) {
    return Camera_1.Camera.findByIdAndDelete(id).lean();
}
// Get summary counts for the dashboard
async function getCameraStats() {
    const stats = await Camera_1.Camera.aggregate([
        { $group: { _id: '$status', count: { $sum: 1 } } },
    ]);
    const result = { total: 0, online: 0, offline: 0, maintenance: 0 };
    stats.forEach(({ _id, count }) => {
        result[_id] = count;
        result.total += count;
    });
    return result;
}
//# sourceMappingURL=camera.repository.js.map