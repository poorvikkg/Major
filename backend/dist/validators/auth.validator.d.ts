/**
 * auth.validator.ts
 * Zod schemas for validating auth request bodies.
 */
import { z } from 'zod';
export declare const loginSchema: z.ZodObject<{
    email: z.ZodString;
    password: z.ZodString;
}, "strip", z.ZodTypeAny, {
    email: string;
    password: string;
}, {
    email: string;
    password: string;
}>;
export declare const registerSchema: z.ZodObject<{
    name: z.ZodString;
    email: z.ZodString;
    password: z.ZodString;
    role: z.ZodDefault<z.ZodLiteral<"viewer">>;
}, "strip", z.ZodTypeAny, {
    name: string;
    email: string;
    password: string;
    role: "viewer";
}, {
    name: string;
    email: string;
    password: string;
    role?: "viewer" | undefined;
}>;
export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
//# sourceMappingURL=auth.validator.d.ts.map