/**
 * recognition.repository.ts
 * Database queries for RecognitionLog and UnknownFace collections.
 */
import { IRecognitionLogDocument } from '../models/RecognitionLog';
import { IUnknownFaceDocument } from '../models/UnknownFace';
import { PaginationOptions } from '../utils/pagination';
export declare function findAllLogs(pagination: PaginationOptions, filter?: Record<string, unknown>): Promise<{
    logs: IRecognitionLogDocument[];
    total: number;
}>;
export declare function createLog(data: Partial<IRecognitionLogDocument>): Promise<IRecognitionLogDocument>;
export declare function countTodayRecognitions(): Promise<number>;
export declare function countUnknownDetections(): Promise<number>;
export declare function getDetectionsByDay(days?: number): Promise<any[]>;
export declare function findAllUnknownFaces(pagination: PaginationOptions): Promise<{
    faces: IUnknownFaceDocument[];
    total: number;
}>;
export declare function createUnknownFace(data: Partial<IUnknownFaceDocument>): Promise<IUnknownFaceDocument>;
//# sourceMappingURL=recognition.repository.d.ts.map