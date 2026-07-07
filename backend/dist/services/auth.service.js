"use strict";
/**
 * auth.service.ts
 * Business logic for authentication: login, register, get current user.
 * Throws AppError for expected failures so the error middleware handles them.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.register = register;
exports.login = login;
exports.getMe = getMe;
const error_middleware_1 = require("../middlewares/error.middleware");
const userRepo = __importStar(require("../repositories/user.repository"));
const jwt_1 = require("../utils/jwt");
// Register a new user (admin-only in production, open for dev/first setup)
async function register(input) {
    const existing = await userRepo.findUserByEmail(input.email);
    if (existing) {
        throw new error_middleware_1.AppError('Email already in use', 409);
    }
    const user = await userRepo.createUser(input);
    const token = (0, jwt_1.signToken)(user._id, user.role);
    return { user: { id: user._id, name: user.name, email: user.email, role: user.role }, token };
}
// Login and return JWT token
async function login(input) {
    const user = await userRepo.findUserByEmail(input.email);
    if (!user) {
        throw new error_middleware_1.AppError('Invalid email or password', 401);
    }
    if (!user.isActive) {
        throw new error_middleware_1.AppError('Your account has been deactivated', 403);
    }
    const isPasswordCorrect = await user.comparePassword(input.password);
    if (!isPasswordCorrect) {
        throw new error_middleware_1.AppError('Invalid email or password', 401);
    }
    // Update last login time
    user.lastLogin = new Date();
    await user.save();
    const token = (0, jwt_1.signToken)(user._id, user.role);
    return {
        user: { id: user._id, name: user.name, email: user.email, role: user.role },
        token,
    };
}
// Get current user profile (called by /auth/me)
async function getMe(userId) {
    const user = await userRepo.findUserById(userId);
    if (!user)
        throw new error_middleware_1.AppError('User not found', 404);
    return user;
}
//# sourceMappingURL=auth.service.js.map