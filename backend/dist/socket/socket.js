"use strict";
/**
 * socket.ts
 * Sets up Socket.IO and registers all event handlers.
 * Real-time features: camera status updates, unknown face alerts, live detection events.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.io = void 0;
exports.initializeSocket = initializeSocket;
exports.emitDetectionEvent = emitDetectionEvent;
exports.emitUnknownFaceAlert = emitUnknownFaceAlert;
exports.emitCameraStatus = emitCameraStatus;
const socket_io_1 = require("socket.io");
const env_1 = require("../config/env");
const logger_1 = require("../config/logger");
let io;
function initializeSocket(httpServer) {
    exports.io = io = new socket_io_1.Server(httpServer, {
        cors: {
            origin: env_1.env.corsOrigin,
            methods: ['GET', 'POST'],
        },
    });
    io.on('connection', (socket) => {
        logger_1.logger.debug({ socketId: socket.id }, 'Socket client connected');
        // Client can join a camera-specific room to receive that camera's events
        socket.on('join-camera', (cameraId) => {
            socket.join(`camera:${cameraId}`);
            logger_1.logger.debug({ cameraId }, 'Socket joined camera room');
        });
        socket.on('leave-camera', (cameraId) => {
            socket.leave(`camera:${cameraId}`);
        });
        socket.on('disconnect', () => {
            logger_1.logger.debug({ socketId: socket.id }, 'Socket client disconnected');
        });
    });
    return io;
}
// Emit a detection event to everyone watching a specific camera
function emitDetectionEvent(cameraId, data) {
    if (io) {
        io.to(`camera:${cameraId}`).emit('detection', data);
    }
}
// Broadcast an unknown face alert to all connected clients
function emitUnknownFaceAlert(data) {
    if (io) {
        io.emit('unknown-face-alert', data);
    }
}
// Broadcast camera status change
function emitCameraStatus(cameraId, status) {
    if (io) {
        io.emit('camera-status', { cameraId, status });
    }
}
//# sourceMappingURL=socket.js.map