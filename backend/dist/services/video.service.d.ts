/**
 * video.service.ts
 * Business logic for video upload and processing status.
 */
import { Types } from 'mongoose';
export declare function getAllVideos(page: number, limit: number, status?: string): Promise<{
    videos: import("../models/Video").IVideoDocument[];
    total: number;
}>;
export declare function getVideoById(id: string): Promise<import("../models/Video").IVideoDocument>;
export declare function saveUploadedVideo(file: Express.Multer.File, userId: Types.ObjectId, cameraId?: string): Promise<import("../models/Video").IVideoDocument>;
export declare function processVideo(videoId: string): Promise<{
    message: string;
    videoId: string;
}>;
export declare function deleteVideo(id: string): Promise<import("../models/Video").IVideoDocument | null>;
//# sourceMappingURL=video.service.d.ts.map