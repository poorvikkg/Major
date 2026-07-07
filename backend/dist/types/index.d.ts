/**
 * index.ts (types)
 * Shared TypeScript interfaces and enums used across the backend.
 * Keeping types in one place makes refactoring easier.
 */
import { Request } from 'express';
import { Types } from 'mongoose';
export type UserRole = 'admin' | 'operator' | 'viewer';
export interface IUser {
    _id: Types.ObjectId;
    name: string;
    email: string;
    password: string;
    role: UserRole;
    avatar?: string;
    isActive: boolean;
    lastLogin?: Date;
    createdAt: Date;
    updatedAt: Date;
}
export type CameraStatus = 'online' | 'offline' | 'maintenance';
export type CameraType = 'ip' | 'rtsp' | 'usb' | 'cloud';
export interface ICamera {
    _id: Types.ObjectId;
    name: string;
    location: string;
    rtspUrl?: string;
    ipAddress?: string;
    type: CameraType;
    status: CameraStatus;
    isActive: boolean;
    lastActive?: Date;
    addedBy: Types.ObjectId;
    createdAt: Date;
    updatedAt: Date;
}
export type VideoStatus = 'uploaded' | 'queued' | 'processing' | 'completed' | 'failed';
export interface IVideo {
    _id: Types.ObjectId;
    filename: string;
    originalName: string;
    mimetype: string;
    size: number;
    duration?: number;
    path: string;
    uploadedBy: Types.ObjectId;
    cameraId?: Types.ObjectId;
    status: VideoStatus;
    processingResult?: object;
    errorMessage?: string;
    createdAt: Date;
    updatedAt: Date;
}
export interface IRecognitionLog {
    _id: Types.ObjectId;
    personName?: string;
    isUnknown: boolean;
    confidence: number;
    cameraId?: Types.ObjectId;
    videoId?: Types.ObjectId;
    snapshot?: string;
    timestamp: Date;
    createdAt: Date;
}
export interface IUnknownFace {
    _id: Types.ObjectId;
    snapshot: string;
    cameraId?: Types.ObjectId;
    videoId?: Types.ObjectId;
    confidence: number;
    isAlerted: boolean;
    timestamp: Date;
    createdAt: Date;
}
export type ComplaintType = 'camera_issue' | 'false_detection' | 'system_error' | 'unauthorized_access' | 'other';
export type ComplaintStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type ComplaintPriority = 'low' | 'medium' | 'high' | 'critical';
export interface IComplaint {
    _id: Types.ObjectId;
    name: string;
    email: string;
    phone?: string;
    type: ComplaintType;
    cameraId?: Types.ObjectId;
    incidentAt: Date;
    description: string;
    attachment?: string;
    priority: ComplaintPriority;
    status: ComplaintStatus;
    assignedTo?: Types.ObjectId;
    remarks?: string;
    createdBy?: Types.ObjectId;
    createdAt: Date;
    updatedAt: Date;
}
export type NotificationType = 'alert' | 'info' | 'warning' | 'success';
export interface INotification {
    _id: Types.ObjectId;
    title: string;
    message: string;
    type: NotificationType;
    userId?: Types.ObjectId;
    isRead: boolean;
    createdAt: Date;
}
export interface AuthRequest extends Request {
    user?: IUser;
}
export interface PaginationMeta {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
}
export interface ApiResponse<T = unknown> {
    success: boolean;
    message: string;
    data?: T;
    pagination?: PaginationMeta;
}
//# sourceMappingURL=index.d.ts.map