/**
 * video.repository.ts
 * Database queries for the Video collection.
 */
import { IVideoDocument } from '../models/Video';
import { PaginationOptions } from '../utils/pagination';
export declare function findAllVideos(pagination: PaginationOptions, filter?: Record<string, unknown>): Promise<{
    videos: IVideoDocument[];
    total: number;
}>;
export declare function findVideoById(id: string): Promise<IVideoDocument | null>;
export declare function createVideo(data: Partial<IVideoDocument>): Promise<IVideoDocument>;
export declare function updateVideoStatus(id: string, status: IVideoDocument['status'], result?: object, errorMessage?: string): Promise<IVideoDocument | null>;
export declare function deleteVideo(id: string): Promise<IVideoDocument | null>;
export declare function countVideos(): Promise<number>;
//# sourceMappingURL=video.repository.d.ts.map