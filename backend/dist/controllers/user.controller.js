"use strict";
/**
 * user.controller.ts
 * Handles HTTP requests for user management (admin only).
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
exports.getAll = getAll;
exports.getOne = getOne;
exports.update = update;
exports.remove = remove;
exports.create = create;
const userService = __importStar(require("../services/user.service"));
const response_1 = require("../utils/response");
const pagination_1 = require("../utils/pagination");
async function getAll(req, res, next) {
    try {
        const { page, limit } = (0, pagination_1.getPaginationOptions)(req);
        const role = req.query.role;
        const { users, total } = await userService.getAllUsers(page, limit, role);
        (0, response_1.sendPaginated)(res, 'Users retrieved', users, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getOne(req, res, next) {
    try {
        const user = await userService.getUserById(req.params.id);
        (0, response_1.sendSuccess)(res, 'User retrieved', user);
    }
    catch (err) {
        next(err);
    }
}
async function update(req, res, next) {
    try {
        const user = await userService.updateUser(req.params.id, req.body);
        (0, response_1.sendSuccess)(res, 'User updated', user);
    }
    catch (err) {
        next(err);
    }
}
async function remove(req, res, next) {
    try {
        await userService.deleteUser(req.params.id);
        (0, response_1.sendSuccess)(res, 'User deactivated');
    }
    catch (err) {
        next(err);
    }
}
async function create(req, res, next) {
    try {
        const user = await userService.createUser(req.body);
        (0, response_1.sendSuccess)(res, 'User created successfully by Administrator', user, 201);
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=user.controller.js.map