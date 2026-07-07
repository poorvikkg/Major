"use strict";
/**
 * user.repository.ts
 * All database queries for the User collection.
 * Services call these functions — they never query Mongoose directly.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.findUserByEmail = findUserByEmail;
exports.findUserById = findUserById;
exports.findAllUsers = findAllUsers;
exports.createUser = createUser;
exports.updateUser = updateUser;
exports.deactivateUser = deactivateUser;
exports.countUsers = countUsers;
const User_1 = require("../models/User");
// Find a user by email (used for login)
async function findUserByEmail(email) {
    return User_1.User.findOne({ email }).select('+password'); // include password for comparison
}
// Find a user by ID
async function findUserById(id) {
    return User_1.User.findById(id).lean();
}
// Get all users with pagination and optional role filter
async function findAllUsers(pagination, role) {
    const filter = role ? { role } : {};
    const [users, total] = await Promise.all([
        User_1.User.find(filter)
            .skip(pagination.skip)
            .limit(pagination.limit)
            .sort({ createdAt: -1 })
            .lean(),
        User_1.User.countDocuments(filter),
    ]);
    return { users: users, total };
}
// Create a new user
async function createUser(data) {
    const user = new User_1.User(data);
    return user.save();
}
// Update a user by ID
async function updateUser(id, data) {
    return User_1.User.findByIdAndUpdate(id, data, { new: true, runValidators: true }).lean();
}
// Soft-delete by deactivating the user
async function deactivateUser(id) {
    return User_1.User.findByIdAndUpdate(id, { isActive: false }, { new: true }).lean();
}
// Count total users (for dashboard stats)
async function countUsers() {
    return User_1.User.countDocuments({ isActive: true });
}
//# sourceMappingURL=user.repository.js.map