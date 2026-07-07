/**
 * complaint.repository.ts
 * Database queries for the Complaint collection.
 */
import { IComplaintDocument } from '../models/Complaint';
import { PaginationOptions } from '../utils/pagination';
export declare function findAllComplaints(pagination: PaginationOptions, filter?: Record<string, unknown>): Promise<{
    complaints: IComplaintDocument[];
    total: number;
}>;
export declare function findComplaintById(id: string): Promise<IComplaintDocument | null>;
export declare function createComplaint(data: Partial<IComplaintDocument>): Promise<IComplaintDocument>;
export declare function updateComplaint(id: string, data: Partial<IComplaintDocument>): Promise<IComplaintDocument | null>;
export declare function deleteComplaint(id: string): Promise<IComplaintDocument | null>;
export declare function countComplaintsByStatus(): Promise<any[]>;
//# sourceMappingURL=complaint.repository.d.ts.map