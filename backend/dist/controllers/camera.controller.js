"use strict";
/**
 * camera.controller.ts
 * Handles HTTP requests for camera management endpoints.
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
exports.getAll = getAll;
exports.getOne = getOne;
exports.create = create;
exports.update = update;
exports.remove = remove;
exports.startCamera = startCamera;
exports.stopCamera = stopCamera;
const cameraService = __importStar(require("../services/camera.service"));
const response_1 = require("../utils/response");
const pagination_1 = require("../utils/pagination");
async function getAll(req, res, next) {
    try {
        const { page, limit, skip } = (0, pagination_1.getPaginationOptions)(req);
        const status = req.query.status;
        const { cameras, total } = await cameraService.getAllCameras(page, limit, status);
        (0, response_1.sendPaginated)(res, 'Cameras retrieved', cameras, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getOne(req, res, next) {
    try {
        const camera = await cameraService.getCameraById(req.params.id);
        (0, response_1.sendSuccess)(res, 'Camera retrieved', camera);
    }
    catch (err) {
        next(err);
    }
}
async function create(req, res, next) {
    try {
        const camera = await cameraService.createCamera(req.body, req.user._id);
        (0, response_1.sendSuccess)(res, 'Camera added successfully', camera, 201);
    }
    catch (err) {
        next(err);
    }
}
async function update(req, res, next) {
    try {
        const camera = await cameraService.updateCamera(req.params.id, req.body);
        (0, response_1.sendSuccess)(res, 'Camera updated successfully', camera);
    }
    catch (err) {
        next(err);
    }
}
async function remove(req, res, next) {
    try {
        await cameraService.deleteCamera(req.params.id);
        (0, response_1.sendSuccess)(res, 'Camera removed successfully');
    }
    catch (err) {
        next(err);
    }
}
async function startCamera(req, res, next) {
    try {
        const camera = await cameraService.startCamera(req.params.id);
        (0, response_1.sendSuccess)(res, 'Camera started', camera);
    }
    catch (err) {
        next(err);
    }
}
async function stopCamera(req, res, next) {
    try {
        const camera = await cameraService.stopCamera(req.params.id);
        (0, response_1.sendSuccess)(res, 'Camera stopped', camera);
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=camera.controller.js.map