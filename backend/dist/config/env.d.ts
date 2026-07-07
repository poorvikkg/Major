/**
 * env.ts
 * Loads and validates environment variables.
 * Crashes the app if required variables are missing — better to fail fast.
 */
export declare const env: {
    port: number;
    nodeEnv: string;
    mongoUri: string;
    jwtSecret: string;
    jwtExpiresIn: string;
    uploadDir: string;
    corsOrigin: string;
    rateLimitWindowMs: number;
    rateLimitMax: number;
    isDev: boolean;
};
//# sourceMappingURL=env.d.ts.map