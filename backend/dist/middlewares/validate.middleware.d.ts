/**
 * validate.middleware.ts
 * Generic Zod validation middleware factory.
 * Pass a Zod schema and it will validate the request body.
 * On failure, it sends a 422 error with field-level messages.
 */
import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';
export declare function validate(schema: ZodSchema): (req: Request, res: Response, next: NextFunction) => void;
//# sourceMappingURL=validate.middleware.d.ts.map