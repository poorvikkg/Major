"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.initializeMinio = initializeMinio;
exports.uploadToMinio = uploadToMinio;
const client_s3_1 = require("@aws-sdk/client-s3");
const env_1 = require("../config/env");
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
// Configure S3 client for MinIO compatibility
const s3Client = new client_s3_1.S3Client({
    endpoint: env_1.env.minio.endpoint,
    region: 'us-east-1', // dummy region
    credentials: {
        accessKeyId: env_1.env.minio.accessKey,
        secretAccessKey: env_1.env.minio.secretKey,
    },
    forcePathStyle: true, // required for MinIO path resolving
});
/**
 * Initializes the MinIO bucket.
 * Creates it if not present, and sets a public read policy so assets load in browser.
 */
async function initializeMinio() {
    const bucketName = env_1.env.minio.bucket;
    try {
        // Check if bucket exists
        await s3Client.send(new client_s3_1.HeadBucketCommand({ Bucket: bucketName }));
        console.log(`[MinIO] Bucket "${bucketName}" is ready.`);
    }
    catch (err) {
        if (err.name === 'NotFound' || err.$metadata?.httpStatusCode === 404) {
            console.log(`[MinIO] Bucket "${bucketName}" not found. Creating bucket...`);
            try {
                await s3Client.send(new client_s3_1.CreateBucketCommand({ Bucket: bucketName }));
                console.log(`[MinIO] Bucket "${bucketName}" created successfully.`);
                // Apply public read access policy
                const policy = {
                    Version: '2012-10-17',
                    Statement: [
                        {
                            Sid: 'PublicReadGetObject',
                            Effect: 'Allow',
                            Principal: '*',
                            Action: ['s3:GetObject'],
                            Resource: [`arn:aws:s3:::${bucketName}/*`],
                        },
                    ],
                };
                await s3Client.send(new client_s3_1.PutBucketPolicyCommand({
                    Bucket: bucketName,
                    Policy: JSON.stringify(policy),
                }));
                console.log(`[MinIO] Public read policy applied to bucket "${bucketName}".`);
            }
            catch (createErr) {
                console.error(`[MinIO] Failed to create and configure bucket:`, createErr);
            }
        }
        else {
            console.error(`[MinIO] Failed to verify bucket status:`, err);
        }
    }
}
/**
 * Uploads a local file to MinIO object storage.
 * Returns the public web URL of the uploaded object.
 * @param localFilePath Path to the file on disk
 * @param destinationFolder S3 directory prefix (e.g. 'attachments')
 */
async function uploadToMinio(localFilePath, destinationFolder = 'attachments') {
    const filename = path_1.default.basename(localFilePath);
    const objectKey = `${destinationFolder}/${filename}`;
    const bucketName = env_1.env.minio.bucket;
    try {
        const fileStream = fs_1.default.createReadStream(localFilePath);
        // Determine content type based on extension
        const ext = path_1.default.extname(filename).toLowerCase();
        let contentType = 'application/octet-stream';
        if (ext === '.jpg' || ext === '.jpeg')
            contentType = 'image/jpeg';
        else if (ext === '.png')
            contentType = 'image/png';
        else if (ext === '.gif')
            contentType = 'image/gif';
        else if (ext === '.mp4')
            contentType = 'video/mp4';
        await s3Client.send(new client_s3_1.PutObjectCommand({
            Bucket: bucketName,
            Key: objectKey,
            Body: fileStream,
            ContentType: contentType,
        }));
        // Return the public web access URL for this object
        // E.g., http://localhost:9000/sentinel-bucket/attachments/attachment_1712345.jpg
        return `${env_1.env.minio.endpoint}/${bucketName}/${objectKey}`;
    }
    catch (err) {
        console.error(`[MinIO] Failed to upload object "${objectKey}":`, err);
        throw err;
    }
}
//# sourceMappingURL=minio.service.js.map