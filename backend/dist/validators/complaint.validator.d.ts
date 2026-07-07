/**
 * complaint.validator.ts
 * Zod schemas for complaint creation and update requests.
 */
import { z } from 'zod';
export declare const createComplaintSchema: z.ZodObject<{
    name: z.ZodString;
    email: z.ZodString;
    phone: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["camera_issue", "false_detection", "system_error", "unauthorized_access", "other"]>;
    cameraId: z.ZodOptional<z.ZodString>;
    incidentAt: z.ZodString;
    description: z.ZodString;
    priority: z.ZodDefault<z.ZodEnum<["low", "medium", "high", "critical"]>>;
}, "strip", z.ZodTypeAny, {
    name: string;
    email: string;
    type: "camera_issue" | "false_detection" | "system_error" | "unauthorized_access" | "other";
    description: string;
    incidentAt: string;
    priority: "low" | "medium" | "high" | "critical";
    cameraId?: string | undefined;
    phone?: string | undefined;
}, {
    name: string;
    email: string;
    type: "camera_issue" | "false_detection" | "system_error" | "unauthorized_access" | "other";
    description: string;
    incidentAt: string;
    cameraId?: string | undefined;
    phone?: string | undefined;
    priority?: "low" | "medium" | "high" | "critical" | undefined;
}>;
export declare const updateComplaintSchema: z.ZodObject<{
    status: z.ZodOptional<z.ZodEnum<["open", "in_progress", "resolved", "closed"]>>;
    assignedTo: z.ZodOptional<z.ZodString>;
    remarks: z.ZodOptional<z.ZodString>;
    priority: z.ZodOptional<z.ZodEnum<["low", "medium", "high", "critical"]>>;
}, "strip", z.ZodTypeAny, {
    status?: "open" | "in_progress" | "resolved" | "closed" | undefined;
    priority?: "low" | "medium" | "high" | "critical" | undefined;
    assignedTo?: string | undefined;
    remarks?: string | undefined;
}, {
    status?: "open" | "in_progress" | "resolved" | "closed" | undefined;
    priority?: "low" | "medium" | "high" | "critical" | undefined;
    assignedTo?: string | undefined;
    remarks?: string | undefined;
}>;
export type CreateComplaintInput = z.infer<typeof createComplaintSchema>;
export type UpdateComplaintInput = z.infer<typeof updateComplaintSchema>;
//# sourceMappingURL=complaint.validator.d.ts.map