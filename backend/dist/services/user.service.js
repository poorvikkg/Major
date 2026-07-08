"use strict";
/**
 * user.service.ts
 * Business logic for user management (admin operations).
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
exports.getAllUsers = getAllUsers;
exports.getUserById = getUserById;
exports.updateUser = updateUser;
exports.deleteUser = deleteUser;
exports.createUser = createUser;
const error_middleware_1 = require("../middlewares/error.middleware");
const userRepo = __importStar(require("../repositories/user.repository"));
async function getAllUsers(page, limit, role) {
    return userRepo.findAllUsers({ page, limit, skip: (page - 1) * limit }, role);
}
async function getUserById(id) {
    const user = await userRepo.findUserById(id);
    if (!user)
        throw new error_middleware_1.AppError('User not found', 404);
    return user;
}
async function updateUser(id, data) {
    // Don't allow changing password through this endpoint
    delete data.password;
    const user = await userRepo.updateUser(id, data);
    if (!user)
        throw new error_middleware_1.AppError('User not found', 404);
    return user;
}
async function deleteUser(id) {
    const user = await userRepo.deactivateUser(id);
    if (!user)
        throw new error_middleware_1.AppError('User not found', 404);
    return user;
}
async function createUser(data) {
    const existingUser = await userRepo.findUserByEmail(data.email);
    if (existingUser)
        throw new error_middleware_1.AppError('Email or Username already exists', 400);
    return userRepo.createUser(data);
}
//# sourceMappingURL=user.service.js.map