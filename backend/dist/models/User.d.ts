/**
 * User.ts
 * Mongoose model for system users.
 * Roles: admin (full access), operator (cameras + uploads), viewer (read-only).
 */
import mongoose, { Document } from 'mongoose';
import { IUser } from '../types';
export interface IUserDocument extends Omit<IUser, '_id'>, Document {
    comparePassword(candidatePassword: string): Promise<boolean>;
}
export declare const User: mongoose.Model<IUserDocument, {}, {}, {}, mongoose.Document<unknown, {}, IUserDocument, {}, {}> & IUserDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=User.d.ts.map