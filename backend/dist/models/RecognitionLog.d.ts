/**
 * RecognitionLog.ts
 * Stores each face detection event from live cameras or uploaded videos.
 * Records who was detected, when, where, and with what confidence.
 */
import mongoose, { Document } from 'mongoose';
import { IRecognitionLog } from '../types';
export interface IRecognitionLogDocument extends Omit<IRecognitionLog, '_id'>, Document {
}
export declare const RecognitionLog: mongoose.Model<IRecognitionLogDocument, {}, {}, {}, mongoose.Document<unknown, {}, IRecognitionLogDocument, {}, {}> & IRecognitionLogDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=RecognitionLog.d.ts.map