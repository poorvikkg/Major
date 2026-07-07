/**
 * SystemLog.ts
 * Audit trail for important system events (logins, config changes, etc.).
 * Helps admins track what happened and who did it.
 */
import mongoose, { Document } from 'mongoose';
export interface ISystemLogDocument extends Document {
    userId?: mongoose.Types.ObjectId;
    action: string;
    resource: string;
    resourceId?: string;
    details?: object;
    ipAddress?: string;
    userAgent?: string;
    createdAt: Date;
}
export declare const SystemLog: mongoose.Model<ISystemLogDocument, {}, {}, {}, mongoose.Document<unknown, {}, ISystemLogDocument, {}, {}> & ISystemLogDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=SystemLog.d.ts.map