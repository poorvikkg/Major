"use strict";
/**
 * notification.service.ts
 * Business logic for user notifications.
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
exports.getNotifications = getNotifications;
exports.markNotificationRead = markNotificationRead;
exports.markAllNotificationsRead = markAllNotificationsRead;
exports.addNotification = addNotification;
const mongoose_1 = require("mongoose");
const notificationRepo = __importStar(require("../repositories/notification.repository"));
const error_middleware_1 = require("../middlewares/error.middleware");
async function getNotifications(userId) {
    const notifications = await notificationRepo.findUserNotifications(userId);
    const unreadCount = await notificationRepo.countUnreadNotifications(userId);
    return { notifications, unreadCount };
}
async function markNotificationRead(id) {
    const notification = await notificationRepo.markAsRead(id);
    if (!notification)
        throw new error_middleware_1.AppError('Notification not found', 404);
    return notification;
}
async function markAllNotificationsRead(userId) {
    await notificationRepo.markAllAsRead(userId);
    return { message: 'All notifications marked as read' };
}
async function addNotification(data) {
    return notificationRepo.createNotification({
        title: data.title,
        message: data.message,
        type: data.type,
        userId: data.userId ? new mongoose_1.Types.ObjectId(data.userId) : undefined,
    });
}
//# sourceMappingURL=notification.service.js.map