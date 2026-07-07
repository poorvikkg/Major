/**
 * Camera.ts
 * Mongoose model for surveillance cameras.
 * Supports IP cameras, RTSP streams, USB cameras, and cloud cameras.
 */
import mongoose, { Document } from 'mongoose';
import { ICamera } from '../types';
export interface ICameraDocument extends Omit<ICamera, '_id'>, Document {
}
export declare const Camera: mongoose.Model<ICameraDocument, {}, {}, {}, mongoose.Document<unknown, {}, ICameraDocument, {}, {}> & ICameraDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=Camera.d.ts.map