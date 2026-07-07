/**
 * dashboard.service.ts
 * Aggregates data from multiple collections for the dashboard overview.
 * Runs queries in parallel using Promise.all for better performance.
 */
export declare function getDashboardStats(): Promise<{
    users: {
        total: number;
    };
    cameras: {
        total: number;
        online: number;
        offline: number;
        maintenance: number;
    };
    videos: {
        processed: number;
    };
    recognitions: {
        today: number;
        unknownDetections: number;
    };
}>;
export declare function getRecentAlerts(limit?: number): Promise<(import("mongoose").FlattenMaps<import("../models/RecognitionLog").IRecognitionLogDocument> & Required<{
    _id: import("mongoose").Types.ObjectId;
}> & {
    __v: number;
})[]>;
export declare function getRecentComplaints(limit?: number): Promise<(import("mongoose").FlattenMaps<import("../models/Complaint").IComplaintDocument> & Required<{
    _id: import("mongoose").Types.ObjectId;
}> & {
    __v: number;
})[]>;
export declare function getRecentActivity(limit?: number): Promise<(import("mongoose").FlattenMaps<import("../models/SystemLog").ISystemLogDocument> & Required<{
    _id: import("mongoose").Types.ObjectId;
}> & {
    __v: number;
})[]>;
//# sourceMappingURL=dashboard.service.d.ts.map