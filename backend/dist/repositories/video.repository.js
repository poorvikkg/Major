"use strict";
/**
 * video.repository.ts
 * Database queries for the Video collection.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.findAllVideos = findAllVideos;
exports.findVideoById = findVideoById;
exports.createVideo = createVideo;
exports.updateVideoStatus = updateVideoStatus;
exports.deleteVideo = deleteVideo;
exports.countVideos = countVideos;
const Video_1 = require("../models/Video");
async function findAllVideos(pagination, filter = {}) {
    const [videos, total] = await Promise.all([
        Video_1.Video.find(filter)
            .populate('uploadedBy', 'name email')
            .populate('cameraId', 'name location')
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ createdAt: -1 })
            .lean(),
        Video_1.Video.countDocuments(filter),
    ]);
    return { videos: videos, total };
}
async function findVideoById(id) {
    return Video_1.Video.findById(id)
        .populate('uploadedBy', 'name email')
        .populate('cameraId', 'name location')
        .lean();
}
async function createVideo(data) {
    const video = new Video_1.Video(data);
    return video.save();
}
async function updateVideoStatus(id, status, result, errorMessage) {
    return Video_1.Video.findByIdAndUpdate(id, { status, processingResult: result, errorMessage }, { new: true }).lean();
}
async function deleteVideo(id) {
    return Video_1.Video.findByIdAndDelete(id).lean();
}
async function countVideos() {
    return Video_1.Video.countDocuments({ status: 'completed' });
}
//# sourceMappingURL=video.repository.js.map