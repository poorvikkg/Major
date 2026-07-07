"use strict";
/**
 * auth.controller.ts
 * Handles HTTP requests for authentication endpoints.
 * Delegates business logic to auth.service.ts.
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
exports.logout = logout;
const authService = __importStar(require("../services/auth.service"));
const response_1 = require("../utils/response");
async function register(req, res, next) {
    try {
        const result = await authService.register(req.body);
        (0, response_1.sendSuccess)(res, 'Account created successfully', result, 201);
    }
    catch (err) {
        next(err);
    }
}
async function login(req, res, next) {
    try {
        const result = await authService.login(req.body);
        (0, response_1.sendSuccess)(res, 'Login successful', result);
    }
    catch (err) {
        next(err);
    }
}
async function getMe(req, res, next) {
    try {
        const user = await authService.getMe(req.user._id.toString());
        (0, response_1.sendSuccess)(res, 'User profile retrieved', user);
    }
    catch (err) {
        next(err);
    }
}
// Logout is handled client-side by removing the JWT token.
// We just send a success response.
function logout(_req, res) {
    (0, response_1.sendSuccess)(res, 'Logged out successfully');
}
//# sourceMappingURL=auth.controller.js.map