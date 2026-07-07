/**
 * auth.service.ts
 * Business logic for authentication: login, register, get current user.
 * Throws AppError for expected failures so the error middleware handles them.
 */
import { LoginInput, RegisterInput } from '../validators/auth.validator';
export declare function register(input: RegisterInput): Promise<{
    user: {
        id: import("mongoose").Types.ObjectId;
        name: string;
        email: string;
        role: import("../types").UserRole;
    };
    token: string;
}>;
export declare function login(input: LoginInput): Promise<{
    user: {
        id: import("mongoose").Types.ObjectId;
        name: string;
        email: string;
        role: import("../types").UserRole;
    };
    token: string;
}>;
export declare function getMe(userId: string): Promise<import("../models/User").IUserDocument>;
//# sourceMappingURL=auth.service.d.ts.map