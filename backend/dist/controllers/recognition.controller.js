"use strict";
/**
 * recognition.controller.ts
 * Handles HTTP requests for recognition logs and unknown faces.
 * Also exposes AI integration endpoints (stubs for now).
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
exports.getLogs = getLogs;
exports.getUnknownFaces = getUnknownFaces;
exports.getAnalytics = getAnalytics;
exports.recognize = recognize;
exports.registerFace = registerFace;
const recognitionService = __importStar(require("../services/recognition.service"));
const response_1 = require("../utils/response");
const pagination_1 = require("../utils/pagination");
async function getLogs(req, res, next) {
    try {
        const { page, limit } = (0, pagination_1.getPaginationOptions)(req);
        const cameraId = req.query.cameraId;
        const { logs, total } = await recognitionService.getLogs(page, limit, cameraId);
        (0, response_1.sendPaginated)(res, 'Recognition logs retrieved', logs, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getUnknownFaces(req, res, next) {
    try {
        const { page, limit } = (0, pagination_1.getPaginationOptions)(req);
        const { faces, total } = await recognitionService.getUnknownFaces(page, limit);
        (0, response_1.sendPaginated)(res, 'Unknown faces retrieved', faces, (0, pagination_1.buildPaginationMeta)(total, page, limit));
    }
    catch (err) {
        next(err);
    }
}
async function getAnalytics(req, res, next) {
    try {
        const days = parseInt(req.query.days) || 7;
        const data = await recognitionService.getDetectionsByDay(days);
        (0, response_1.sendSuccess)(res, 'Analytics data retrieved', data);
    }
    catch (err) {
        next(err);
    }
}
// AI Integration Point — called by the Python AI service
async function recognize(req, res, next) {
    try {
        const result = await recognitionService.recognize(req.body.image);
        (0, response_1.sendSuccess)(res, 'Recognition result', result);
    }
    catch (err) {
        next(err);
    }
}
// AI Integration Point — register a new face
async function registerFace(req, res, next) {
    try {
        const result = await recognitionService.registerFace(req.body);
        (0, response_1.sendSuccess)(res, 'Face registration queued', result);
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=recognition.controller.js.map