"use strict";
/**
 * complaint.routes.ts
 * Routes for complaint submission and management.
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
const express_1 = require("express");
const complaintController = __importStar(require("../controllers/complaint.controller"));
const auth_middleware_1 = require("../middlewares/auth.middleware");
const role_middleware_1 = require("../middlewares/role.middleware");
const validate_middleware_1 = require("../middlewares/validate.middleware");
const complaint_validator_1 = require("../validators/complaint.validator");
const upload_middleware_1 = require("../middlewares/upload.middleware");
const router = (0, express_1.Router)();
router.use(auth_middleware_1.authenticate);
router.get('/', complaintController.getAll);
router.get('/stats', complaintController.getStats);
router.get('/:id', complaintController.getOne);
// Any authenticated user can submit a complaint
router.post('/', upload_middleware_1.uploadAttachment.single('attachment'), (0, validate_middleware_1.validate)(complaint_validator_1.createComplaintSchema), complaintController.create);
// Only admins and operators can update complaints
router.put('/:id', (0, role_middleware_1.requireRole)('admin', 'operator'), (0, validate_middleware_1.validate)(complaint_validator_1.updateComplaintSchema), complaintController.update);
router.delete('/:id', (0, role_middleware_1.requireRole)('admin'), complaintController.remove);
exports.default = router;
//# sourceMappingURL=complaint.routes.js.map