/**
 * jwt.ts
 * Utility functions for creating and verifying JWT tokens.
 * Keeps all JWT logic in one place for easy auditing.
 */
import { Types } from 'mongoose';
interface TokenPayload {
    userId: string;
    role: string;
}
export declare function signToken(userId: Types.ObjectId, role: string): string;
export declare function verifyToken(token: string): TokenPayload | null;
export {};
//# sourceMappingURL=jwt.d.ts.map