"use strict";
/**
 * jwt.ts
 * Utility functions for creating and verifying JWT tokens.
 * Keeps all JWT logic in one place for easy auditing.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.signToken = signToken;
exports.verifyToken = verifyToken;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const env_1 = require("../config/env");
// Generate a signed JWT for a user
function signToken(userId, role) {
    return jsonwebtoken_1.default.sign({ userId: userId.toString(), role }, env_1.env.jwtSecret, { expiresIn: env_1.env.jwtExpiresIn });
}
// Verify a token and return its payload, or null if invalid
function verifyToken(token) {
    try {
        return jsonwebtoken_1.default.verify(token, env_1.env.jwtSecret);
    }
    catch {
        return null; // token is expired, tampered, or invalid
    }
}
//# sourceMappingURL=jwt.js.map