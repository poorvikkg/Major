/**
 * socket.ts
 * Sets up Socket.IO and registers all event handlers.
 * Real-time features: camera status updates, unknown face alerts, live detection events.
 */
import { Server as HttpServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
declare let io: SocketIOServer;
export declare function initializeSocket(httpServer: HttpServer): SocketIOServer;
export declare function emitDetectionEvent(cameraId: string, data: object): void;
export declare function emitUnknownFaceAlert(data: object): void;
export declare function emitCameraStatus(cameraId: string, status: string): void;
export { io };
//# sourceMappingURL=socket.d.ts.map