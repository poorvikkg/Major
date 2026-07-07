/**
 * Complaint.ts
 * Stores user-submitted complaints about camera issues or incidents.
 * Supports priority, status tracking, and assignment to operators/admins.
 */
import mongoose, { Document } from 'mongoose';
import { IComplaint } from '../types';
export interface IComplaintDocument extends Omit<IComplaint, '_id'>, Document {
}
export declare const Complaint: mongoose.Model<IComplaintDocument, {}, {}, {}, mongoose.Document<unknown, {}, IComplaintDocument, {}, {}> & IComplaintDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=Complaint.d.ts.map