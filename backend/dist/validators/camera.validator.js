"use strict";
/**
 * camera.validator.ts
 * Zod schemas for camera CRUD requests.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateCameraSchema = exports.createCameraSchema = void 0;
const zod_1 = require("zod");
exports.createCameraSchema = zod_1.z.object({
    name: zod_1.z.string().min(2).max(100),
    location: zod_1.z.string().min(2).max(200),
    rtspUrl: zod_1.z.string().url().optional(),
    ipAddress: zod_1.z.string().optional(),
    type: zod_1.z.enum(['ip', 'rtsp', 'usb', 'cloud']),
    status: zod_1.z.enum(['online', 'offline', 'maintenance']).default('offline'),
    isActive: zod_1.z.boolean().default(true),
});
exports.updateCameraSchema = exports.createCameraSchema.partial();
//# sourceMappingURL=camera.validator.js.map