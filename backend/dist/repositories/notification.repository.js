"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.findUserNotifications = findUserNotifications;
exports.countUnreadNotifications = countUnreadNotifications;
exports.markAsRead = markAsRead;
exports.markAllAsRead = markAllAsRead;
exports.createNotification = createNotification;
const Notification_1 = require("../models/Notification");
const mongoose_1 = require("mongoose");
async function findUserNotifications(userId, limit = 20) {
    return Notification_1.Notification.find({
        $or: [{ userId: new mongoose_1.Types.ObjectId(userId) }, { userId: { $exists: false } }],
    })
        .sort({ createdAt: -1 })
        .limit(limit)
        .exec();
}
async function countUnreadNotifications(userId) {
    return Notification_1.Notification.countDocuments({
        $or: [{ userId: new mongoose_1.Types.ObjectId(userId) }, { userId: { $exists: false } }],
        isRead: false,
    }).exec();
}
async function markAsRead(id) {
    return Notification_1.Notification.findByIdAndUpdate(id, { isRead: true }, { new: true }).exec();
}
async function markAllAsRead(userId) {
    await Notification_1.Notification.updateMany({
        $or: [{ userId: new mongoose_1.Types.ObjectId(userId) }, { userId: { $exists: false } }],
        isRead: false,
    }, { isRead: true }).exec();
}
async function createNotification(data) {
    return Notification_1.Notification.create(data);
}
//# sourceMappingURL=notification.repository.js.map