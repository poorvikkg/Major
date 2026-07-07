/**
 * complaint.service.ts
 * Business logic for complaint creation and management.
 */
import { CreateComplaintInput, UpdateComplaintInput } from '../validators/complaint.validator';
import { Types } from 'mongoose';
export declare function getAllComplaints(page: number, limit: number, status?: string, priority?: string): Promise<{
    complaints: import("../models/Complaint").IComplaintDocument[];
    total: number;
}>;
export declare function getComplaintById(id: string): Promise<import("../models/Complaint").IComplaintDocument>;
export declare function createComplaint(input: CreateComplaintInput, userId?: Types.ObjectId): Promise<import("../models/Complaint").IComplaintDocument>;
export declare function updateComplaint(id: string, input: UpdateComplaintInput): Promise<import("../models/Complaint").IComplaintDocument>;
export declare function deleteComplaint(id: string): Promise<import("../models/Complaint").IComplaintDocument>;
export declare function getComplaintStats(): Promise<any>;
//# sourceMappingURL=complaint.service.d.ts.map