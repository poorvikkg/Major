/**
 * recognition.service.ts
 * Business logic for recognition logs and unknown face alerts.
 */
export declare function getLogs(page: number, limit: number, cameraId?: string, videoId?: string): Promise<{
    logs: import("../models/RecognitionLog").IRecognitionLogDocument[];
    total: number;
}>;
export declare function getUnknownFaces(page: number, limit: number): Promise<{
    faces: import("../models/UnknownFace").IUnknownFaceDocument[];
    total: number;
}>;
export declare function getDetectionsByDay(days: number): Promise<any[]>;
export declare function logRecognition(data: {
    personName?: string;
    isUnknown: boolean;
    confidence: number;
    cameraId?: string;
    videoId?: string;
    snapshot?: string;
    timestamp?: Date;
}): Promise<import("../models/RecognitionLog").IRecognitionLogDocument>;
export declare function registerFace(_data: {
    name: string;
    images: string[];
}): Promise<{
    message: string;
}>;
export declare function recognize(_imageBase64: string): Promise<{
    message: string;
}>;
//# sourceMappingURL=recognition.service.d.ts.map