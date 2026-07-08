"use strict";
/**
 * video.routes.ts
 * Routes for video upload, listing, and processing.
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
const videoController = __importStar(require("../controllers/video.controller"));
const auth_middleware_1 = require("../middlewares/auth.middleware");
const role_middleware_1 = require("../middlewares/role.middleware");
const upload_middleware_1 = require("../middlewares/upload.middleware");
const router = (0, express_1.Router)();
router.use(auth_middleware_1.authenticate);
router.get('/', videoController.getAll);
router.get('/:id', videoController.getOne);
// Operators and admins can upload videos
router.post('/upload', (0, role_middleware_1.requireRole)('admin', 'operator'), upload_middleware_1.uploadVideo.single('video'), videoController.upload);
// One-shot: upload + immediately queue for face recognition analysis
router.post('/analyse', (0, role_middleware_1.requireRole)('admin', 'operator', 'viewer'), upload_middleware_1.uploadVideo.single('video'), videoController.analyseVideo);
// AI integration: queue a video for processing
router.post('/process', (0, role_middleware_1.requireRole)('admin', 'operator'), videoController.processVideo);
router.delete('/:id', (0, role_middleware_1.requireRole)('admin', 'operator'), videoController.remove);
exports.default = router;
//# sourceMappingURL=video.routes.js.map