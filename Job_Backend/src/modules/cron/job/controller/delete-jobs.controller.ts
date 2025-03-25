import '@core/declarations'
import { deleteAllRelatedJobs } from '@core/field-mapping'
import { JobPortals } from '@models/raw-job.model'


export default async function DeleteJobs() {
	try {
		const rawJobs = await App.Models.RawJob.find({
			isDeleted: true,
		}).limit(1)
		if (rawJobs.length) {
			Logger.info('Cron: Raw data found for delete the jobs')
			for (const rawJob of rawJobs) {
				const { portal, rawData } = rawJob
				Logger.info(`Deleted job id : ${rawData.id}`)
				if (portal == JobPortals.Naukri) {
					const jobId = rawData.id
					if (jobId) {
						const job = await App.Models.Job.findOne({
							id: jobId,
							portal: JobPortals.Naukri,
						})
						if (job) {
							const _job = job._id
							await deleteAllRelatedJobs(_job)

							// Delete the job from raw collection
							await App.Models.RawJob.deleteOne({
								'rawData.id': jobId,
								portal: JobPortals.Naukri,
							})
						}
					}
				}
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
