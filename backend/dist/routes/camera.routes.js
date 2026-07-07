"use strict";
/**
 * camera.routes.ts
 * Routes for camera CRUD and AI control (start/stop).
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
const express_1 = require("express");
const cameraController = __importStar(require("../controllers/camera.controller"));
const auth_middleware_1 = require("../middlewares/auth.middleware");
const role_middleware_1 = require("../middlewares/role.middleware");
const validate_middleware_1 = require("../middlewares/validate.middleware");
const camera_validator_1 = require("../validators/camera.validator");
const router = (0, express_1.Router)();
// All camera routes require authentication
router.use(auth_middleware_1.authenticate);
router.get('/', cameraController.getAll);
router.get('/:id', cameraController.getOne);
// Only admin and operator can add/edit/delete cameras
router.post('/', (0, role_middleware_1.requireRole)('admin', 'operator'), (0, validate_middleware_1.validate)(camera_validator_1.createCameraSchema), cameraController.create);
router.put('/:id', (0, role_middleware_1.requireRole)('admin', 'operator'), (0, validate_middleware_1.validate)(camera_validator_1.updateCameraSchema), cameraController.update);
router.delete('/:id', (0, role_middleware_1.requireRole)('admin'), cameraController.remove);
// AI integration endpoints
router.post('/:id/start', (0, role_middleware_1.requireRole)('admin', 'operator'), cameraController.startCamera);
router.post('/:id/stop', (0, role_middleware_1.requireRole)('admin', 'operator'), cameraController.stopCamera);
exports.default = router;
//# sourceMappingURL=camera.routes.js.map