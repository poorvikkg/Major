/**
 * Video.ts
 * Mongoose model for uploaded surveillance videos.
 * Tracks upload details and AI processing status.
 */
import mongoose, { Document } from 'mongoose';
import { IVideo } from '../types';
export interface IVideoDocument extends Omit<IVideo, '_id'>, Document {
}
export declare const Video: mongoose.Model<IVideoDocument, {}, {}, {}, mongoose.Document<unknown, {}, IVideoDocument, {}, {}> & IVideoDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=Video.d.ts.map