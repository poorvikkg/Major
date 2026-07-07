"use strict";
/**
 * validate.middleware.ts
 * Generic Zod validation middleware factory.
 * Pass a Zod schema and it will validate the request body.
 * On failure, it sends a 422 error with field-level messages.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.validate = validate;
function validate(schema) {
    return (req, res, next) => {
        const result = schema.safeParse(req.body);
        if (!result.success) {
            // Format Zod errors into a readable message
            const errors = result.error.errors.map((e) => ({
                field: e.path.join('.'),
                message: e.message,
            }));
            res.status(422).json({
                success: false,
                message: 'Validation failed',
                errors,
            });
            return;
        }
        // Replace req.body with the validated + typed data
        req.body = result.data;
        next();
    };
}
//# sourceMappingURL=validate.middleware.js.map