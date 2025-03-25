import AWS from 'aws-sdk'

const BUCKET_NAME = App.Config.AWS.S3_BUCKET_NAME

AWS.config.update({
	region: App.Config.AWS.REGION,
	accessKeyId: App.Config.AWS.ACCESS_KEY,
	secretAccessKey: App.Config.AWS.SECRET_KEY,
})

class AwsS3Helper {
	private s3: any

	constructor() {
		this.s3 = new AWS.S3()
	}

	/**
	 * Stores user data from all collections to an S3 bucket in JSON format.
	 */
	async storeDataToS3({
		folderName,
		fileName,
		bucket = BUCKET_NAME,
		isPublic = true,
		data,
	}: {
		folderName: string
		fileName: string
		bucket?: string
		isPublic?: boolean
		data: any
	}) {
		try {
			const filePath = `${folderName}/${fileName}`

			// Prepare S3 upload parameters
			const params = {
				Bucket: bucket,
				Key: filePath,
				Body: data,
				ACL: isPublic ? 'public-read' : 'private',
				ContentType: 'application/json',
			}

			// Upload the file to S3
			const stored = await this.s3.upload(params).promise()

			return {
				isSuccess: true,
				data: {
					key: stored.Key,
					url: stored.Location,
				},
			}
		} catch (error) {
			Logger.error(`${error?.message}`)
			return { isSuccess: false, data: error }
		}
	}
}

export const S3Helper = new AwsS3Helper()
