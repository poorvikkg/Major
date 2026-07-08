/**
 * notification.service.ts
 * Business logic for user notifications.
 */
export declare function getNotifications(userId: string): Promise<{
    notifications: import("../models/Notification").INotificationDocument[];
    unreadCount: number;
}>;
export declare function markNotificationRead(id: string): Promise<import("../models/Notification").INotificationDocument>;
export declare function markAllNotificationsRead(userId: string): Promise<{
    message: string;
}>;
export declare function addNotification(data: {
    title: string;
    message: string;
    type?: 'alert' | 'info' | 'warning' | 'success';
    userId?: string;
}): Promise<import("../models/Notification").INotificationDocument>;
//# sourceMappingURL=notification.service.d.ts.map