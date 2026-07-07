/**
 * user.repository.ts
 * All database queries for the User collection.
 * Services call these functions — they never query Mongoose directly.
 */
import { IUserDocument } from '../models/User';
import { PaginationOptions } from '../utils/pagination';
export declare function findUserByEmail(email: string): Promise<IUserDocument | null>;
export declare function findUserById(id: string): Promise<IUserDocument | null>;
export declare function findAllUsers(pagination: PaginationOptions, role?: string): Promise<{
    users: IUserDocument[];
    total: number;
}>;
export declare function createUser(data: Partial<IUserDocument>): Promise<IUserDocument>;
export declare function updateUser(id: string, data: Partial<IUserDocument>): Promise<IUserDocument | null>;
export declare function deactivateUser(id: string): Promise<IUserDocument | null>;
export declare function countUsers(): Promise<number>;
//# sourceMappingURL=user.repository.d.ts.map