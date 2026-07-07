"use strict";
/**
 * auth.middleware.ts
 * Checks that the request has a valid JWT token.
 * Attaches the user object to req.user for downstream handlers.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.authenticate = authenticate;
const jwt_1 = require("../utils/jwt");
const User_1 = require("../models/User");
const response_1 = require("../utils/response");
async function authenticate(req, res, next) {
    // Extract token from Authorization header: "Bearer <token>"
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        (0, response_1.sendError)(res, 'No token provided', 401);
        return;
    }
    const token = authHeader.split(' ')[1];
    const payload = (0, jwt_1.verifyToken)(token);
    if (!payload) {
        (0, response_1.sendError)(res, 'Invalid or expired token', 401);
        return;
    }
    // Load the full user from the DB to get the latest role and isActive status
    const user = await User_1.User.findById(payload.userId).select('+password').lean();
    if (!user || !user.isActive) {
        (0, response_1.sendError)(res, 'Account not found or deactivated', 401);
        return;
    }
    req.user = user;
    next();
}
//# sourceMappingURL=auth.middleware.js.map