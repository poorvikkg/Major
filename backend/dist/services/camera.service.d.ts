/**
 * camera.service.ts
 * Business logic for camera management.
 */
import { CreateCameraInput, UpdateCameraInput } from '../validators/camera.validator';
import { Types } from 'mongoose';
export declare function getAllCameras(page: number, limit: number, status?: string): Promise<{
    cameras: import("../models/Camera").ICameraDocument[];
    total: number;
}>;
export declare function getCameraById(id: string): Promise<import("../models/Camera").ICameraDocument>;
export declare function createCamera(input: CreateCameraInput, userId: Types.ObjectId): Promise<import("../models/Camera").ICameraDocument>;
export declare function updateCamera(id: string, input: UpdateCameraInput): Promise<import("../models/Camera").ICameraDocument>;
export declare function deleteCamera(id: string): Promise<import("../models/Camera").ICameraDocument>;
export declare function getCameraStats(): Promise<{
    total: number;
    online: number;
    offline: number;
    maintenance: number;
}>;
export declare function startCamera(id: string): Promise<import("../models/Camera").ICameraDocument | null>;
export declare function stopCamera(id: string): Promise<import("../models/Camera").ICameraDocument | null>;
//# sourceMappingURL=camera.service.d.ts.map