/**
 * Initializes the MinIO bucket.
 * Creates it if not present, and sets a public read policy so assets load in browser.
 */
export declare function initializeMinio(): Promise<void>;
/**
 * Uploads a local file to MinIO object storage.
 * Returns the public web URL of the uploaded object.
 * @param localFilePath Path to the file on disk
 * @param destinationFolder S3 directory prefix (e.g. 'attachments')
 */
export declare function uploadToMinio(localFilePath: string, destinationFolder?: string): Promise<string>;
//# sourceMappingURL=minio.service.d.ts.map