import '@core/declarations'
import constant from '@core/constants'
import { encrypt } from '@helpers/crypto.helper'
import { S3Helper } from '@helpers/aws-s3.helper';


export async function UploadJobsDataToS3(
	_job: string
): Promise<{ isSuccess: boolean; error?: string }> {
	try {
		const [
            appliedJobs,
            jobMatchReason,
			notInterestedJobs,
			reportedJobs,
            savedJobs,
            job
			
		] = await Promise.all([
			App.Models.AppliedJob.find({ _job }).lean(),
			App.Models.JobMatchReason.find({ _job }).lean(),
			App.Models.NotInterestedJob.find({ _job }).lean(),
			App.Models.ReportJob.find({ _job }).lean(),
			App.Models.SavedJob.find({ _job }).lean(),
			App.Models.Job.findById(_job).lean(),
		])

		const datasets = {
            AppliedJobs: appliedJobs,
            JobMatchReason: jobMatchReason,
			SavedJobs: savedJobs,
			NotInterestedJobs: notInterestedJobs,
            ReportedJobs: reportedJobs,
            Job: job
		}

		for (const [collectionName, data] of Object.entries(datasets)) {
			if (!data || (Array.isArray(data) && data.length === 0)) {
				continue
			}
			const jsonData = JSON.stringify(data, null, 2)
			const encryptedJobId = encrypt(_job)
			const fileName = `${collectionName.toLowerCase()}.json`
			const folderName = `${constant.AWS.S3.BUCKET_FOLDERS.DELETED_JOBS}/${encryptedJobId}`
			const uploadResponse = await S3Helper.storeDataToS3({
				folderName,
				fileName,
				data: jsonData,
			})

			if (!uploadResponse.isSuccess) {
				return { isSuccess: false, error: `Failed to upload ${collectionName} data.` }
			}
		}
		return { isSuccess: true }
	} catch (error) {
		Logger.error(`${error?.message}`)
		return { isSuccess: false, error: error?.message ?? 'Unknown error' }
	}
}
