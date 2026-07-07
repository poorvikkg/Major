"use strict";
/**
 * camera.service.ts
 * Business logic for camera management.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAllCameras = getAllCameras;
exports.getCameraById = getCameraById;
exports.createCamera = createCamera;
exports.updateCamera = updateCamera;
exports.deleteCamera = deleteCamera;
exports.getCameraStats = getCameraStats;
exports.startCamera = startCamera;
exports.stopCamera = stopCamera;
const error_middleware_1 = require("../middlewares/error.middleware");
const cameraRepo = __importStar(require("../repositories/camera.repository"));
async function getAllCameras(page, limit, status) {
    const filter = status ? { status } : {};
    return cameraRepo.findAllCameras({ page, limit, skip: (page - 1) * limit }, filter);
}
async function getCameraById(id) {
    const camera = await cameraRepo.findCameraById(id);
    if (!camera)
        throw new error_middleware_1.AppError('Camera not found', 404);
    return camera;
}
async function createCamera(input, userId) {
    return cameraRepo.createCamera({ ...input, addedBy: userId });
}
async function updateCamera(id, input) {
    const camera = await cameraRepo.updateCamera(id, input);
    if (!camera)
        throw new error_middleware_1.AppError('Camera not found', 404);
    return camera;
}
async function deleteCamera(id) {
    const camera = await cameraRepo.deleteCamera(id);
    if (!camera)
        throw new error_middleware_1.AppError('Camera not found', 404);
    return camera;
}
async function getCameraStats() {
    return cameraRepo.getCameraStats();
}
// AI Integration Point: will communicate with Python FastAPI later
async function startCamera(id) {
    const camera = await cameraRepo.findCameraById(id);
    if (!camera)
        throw new error_middleware_1.AppError('Camera not found', 404);
    // TODO: POST to Python AI service: http://ai-service/api/cameras/start
    // For now, just update status to online
    return cameraRepo.updateCamera(id, { status: 'online', lastActive: new Date() });
}
// AI Integration Point
async function stopCamera(id) {
    const camera = await cameraRepo.findCameraById(id);
    if (!camera)
        throw new error_middleware_1.AppError('Camera not found', 404);
    // TODO: POST to Python AI service: http://ai-service/api/cameras/stop
    return cameraRepo.updateCamera(id, { status: 'offline' });
}
//# sourceMappingURL=camera.service.js.map