/**
 * camera.validator.ts
 * Zod schemas for camera CRUD requests.
 */
import { z } from 'zod';
export declare const createCameraSchema: z.ZodObject<{
    name: z.ZodString;
    location: z.ZodString;
    rtspUrl: z.ZodOptional<z.ZodString>;
    ipAddress: z.ZodOptional<z.ZodString>;
    type: z.ZodEnum<["ip", "rtsp", "usb", "cloud"]>;
    status: z.ZodDefault<z.ZodEnum<["online", "offline", "maintenance"]>>;
    isActive: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    name: string;
    isActive: boolean;
    type: "ip" | "rtsp" | "usb" | "cloud";
    status: "online" | "offline" | "maintenance";
    location: string;
    rtspUrl?: string | undefined;
    ipAddress?: string | undefined;
}, {
    name: string;
    type: "ip" | "rtsp" | "usb" | "cloud";
    location: string;
    isActive?: boolean | undefined;
    status?: "online" | "offline" | "maintenance" | undefined;
    rtspUrl?: string | undefined;
    ipAddress?: string | undefined;
}>;
export declare const updateCameraSchema: z.ZodObject<{
    name: z.ZodOptional<z.ZodString>;
    location: z.ZodOptional<z.ZodString>;
    rtspUrl: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    ipAddress: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    type: z.ZodOptional<z.ZodEnum<["ip", "rtsp", "usb", "cloud"]>>;
    status: z.ZodOptional<z.ZodDefault<z.ZodEnum<["online", "offline", "maintenance"]>>>;
    isActive: z.ZodOptional<z.ZodDefault<z.ZodBoolean>>;
}, "strip", z.ZodTypeAny, {
    name?: string | undefined;
    isActive?: boolean | undefined;
    type?: "ip" | "rtsp" | "usb" | "cloud" | undefined;
    status?: "online" | "offline" | "maintenance" | undefined;
    location?: string | undefined;
    rtspUrl?: string | undefined;
    ipAddress?: string | undefined;
}, {
    name?: string | undefined;
    isActive?: boolean | undefined;
    type?: "ip" | "rtsp" | "usb" | "cloud" | undefined;
    status?: "online" | "offline" | "maintenance" | undefined;
    location?: string | undefined;
    rtspUrl?: string | undefined;
    ipAddress?: string | undefined;
}>;
export type CreateCameraInput = z.infer<typeof createCameraSchema>;
export type UpdateCameraInput = z.infer<typeof updateCameraSchema>;
//# sourceMappingURL=camera.validator.d.ts.map