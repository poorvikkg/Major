"use strict";
/**
 * index.ts (routes)
 * Aggregates all route modules into a single router.
 * This is the only file imported by app.ts.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const auth_routes_1 = __importDefault(require("./auth.routes"));
const camera_routes_1 = __importDefault(require("./camera.routes"));
const video_routes_1 = __importDefault(require("./video.routes"));
const recognition_routes_1 = __importDefault(require("./recognition.routes"));
const complaint_routes_1 = __importDefault(require("./complaint.routes"));
const dashboard_routes_1 = __importDefault(require("./dashboard.routes"));
const user_routes_1 = __importDefault(require("./user.routes"));
const notification_routes_1 = __importDefault(require("./notification.routes"));
const job_routes_1 = __importDefault(require("./job.routes"));
const router = (0, express_1.Router)();
// Mount each route module at its API prefix
router.use('/auth', auth_routes_1.default);
router.use('/cameras', camera_routes_1.default);
router.use('/videos', video_routes_1.default);
router.use('/recognition', recognition_routes_1.default);
router.use('/complaints', complaint_routes_1.default);
router.use('/dashboard', dashboard_routes_1.default);
router.use('/users', user_routes_1.default);
router.use('/notifications', notification_routes_1.default);
router.use('/jobs', job_routes_1.default);
exports.default = router;
//# sourceMappingURL=index.js.map