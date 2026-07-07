"use strict";
/**
 * role.middleware.ts
 * Factory function that returns a middleware to check if the user
 * has one of the required roles. Always use AFTER authenticate middleware.
 *
 * Usage: router.get('/admin', authenticate, requireRole('admin'), handler)
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.requireRole = requireRole;
const response_1 = require("../utils/response");
function requireRole(...roles) {
    return (req, res, next) => {
        if (!req.user) {
            (0, response_1.sendError)(res, 'Not authenticated', 401);
            return;
        }
        if (!roles.includes(req.user.role)) {
            (0, response_1.sendError)(res, 'You do not have permission to perform this action', 403);
            return;
        }
        next();
    };
}
//# sourceMappingURL=role.middleware.js.map