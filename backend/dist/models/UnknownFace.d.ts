/**
 * UnknownFace.ts
 * Stores face detections where the person is not in the database.
 * Used for the unknown faces alert gallery in the UI.
 */
import mongoose, { Document } from 'mongoose';
import { IUnknownFace } from '../types';
export interface IUnknownFaceDocument extends Omit<IUnknownFace, '_id'>, Document {
}
export declare const UnknownFace: mongoose.Model<IUnknownFaceDocument, {}, {}, {}, mongoose.Document<unknown, {}, IUnknownFaceDocument, {}, {}> & IUnknownFaceDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=UnknownFace.d.ts.map