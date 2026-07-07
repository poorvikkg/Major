/**
 * user.service.ts
 * Business logic for user management (admin operations).
 */
export declare function getAllUsers(page: number, limit: number, role?: string): Promise<{
    users: import("../models/User").IUserDocument[];
    total: number;
}>;
export declare function getUserById(id: string): Promise<import("../models/User").IUserDocument>;
export declare function updateUser(id: string, data: Record<string, unknown>): Promise<import("../models/User").IUserDocument>;
export declare function deleteUser(id: string): Promise<import("../models/User").IUserDocument>;
//# sourceMappingURL=user.service.d.ts.map