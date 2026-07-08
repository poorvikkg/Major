"use strict";
/**
 * complaint.validator.ts
 * Zod schemas for complaint creation and update requests.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateComplaintSchema = exports.createComplaintSchema = void 0;
const zod_1 = require("zod");
exports.createComplaintSchema = zod_1.z.object({
    name: zod_1.z.string().min(2).max(100),
    email: zod_1.z.string().email(),
    phone: zod_1.z.string().optional(),
    type: zod_1.z.enum(['camera_issue', 'false_detection', 'system_error', 'unauthorized_access', 'other']),
    cameraId: zod_1.z.string().optional(),
    incidentAt: zod_1.z.string().datetime({ message: 'Invalid date/time format' }),
    description: zod_1.z.string().min(10, 'Description must be at least 10 characters').max(2000),
    priority: zod_1.z.enum(['low', 'medium', 'high', 'critical']).default('medium'),
    attachments: zod_1.z.array(zod_1.z.string()).optional(),
});
exports.updateComplaintSchema = zod_1.z.object({
    status: zod_1.z.enum(['open', 'in_progress', 'resolved', 'closed']).optional(),
    assignedTo: zod_1.z.string().optional(),
    remarks: zod_1.z.string().max(1000).optional(),
    priority: zod_1.z.enum(['low', 'medium', 'high', 'critical']).optional(),
});
//# sourceMappingURL=complaint.validator.js.map