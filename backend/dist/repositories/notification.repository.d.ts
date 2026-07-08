import { INotificationDocument } from '../models/Notification';
export declare function findUserNotifications(userId: string, limit?: number): Promise<INotificationDocument[]>;
export declare function countUnreadNotifications(userId: string): Promise<number>;
export declare function markAsRead(id: string): Promise<INotificationDocument | null>;
export declare function markAllAsRead(userId: string): Promise<void>;
export declare function createNotification(data: Partial<INotificationDocument>): Promise<INotificationDocument>;
//# sourceMappingURL=notification.repository.d.ts.map