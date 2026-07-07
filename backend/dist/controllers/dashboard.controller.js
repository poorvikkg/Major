"use strict";
/**
 * dashboard.controller.ts
 * Handles requests for dashboard data (stats, alerts, activity).
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
exports.getStats = getStats;
exports.getRecentAlerts = getRecentAlerts;
exports.getRecentActivity = getRecentActivity;
const dashboardService = __importStar(require("../services/dashboard.service"));
const response_1 = require("../utils/response");
async function getStats(req, res, next) {
    try {
        const stats = await dashboardService.getDashboardStats();
        (0, response_1.sendSuccess)(res, 'Dashboard stats retrieved', stats);
    }
    catch (err) {
        next(err);
    }
}
async function getRecentAlerts(req, res, next) {
    try {
        const alerts = await dashboardService.getRecentAlerts(5);
        (0, response_1.sendSuccess)(res, 'Recent alerts retrieved', alerts);
    }
    catch (err) {
        next(err);
    }
}
async function getRecentActivity(req, res, next) {
    try {
        const activity = await dashboardService.getRecentActivity(10);
        (0, response_1.sendSuccess)(res, 'Recent activity retrieved', activity);
    }
    catch (err) {
        next(err);
    }
}
//# sourceMappingURL=dashboard.controller.js.map