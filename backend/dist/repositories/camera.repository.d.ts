/**
 * camera.repository.ts
 * Database queries for the Camera collection.
 */
import { ICameraDocument } from '../models/Camera';
import { PaginationOptions } from '../utils/pagination';
export declare function findAllCameras(pagination: PaginationOptions, filter?: Record<string, unknown>): Promise<{
    cameras: ICameraDocument[];
    total: number;
}>;
export declare function findCameraById(id: string): Promise<ICameraDocument | null>;
export declare function createCamera(data: Partial<ICameraDocument>): Promise<ICameraDocument>;
export declare function updateCamera(id: string, data: Partial<ICameraDocument>): Promise<ICameraDocument | null>;
export declare function deleteCamera(id: string): Promise<ICameraDocument | null>;
export declare function getCameraStats(): Promise<{
    total: number;
    online: number;
    offline: number;
    maintenance: number;
}>;
//# sourceMappingURL=camera.repository.d.ts.map