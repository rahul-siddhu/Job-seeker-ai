import '@core/declarations'
import { I_Job } from '@models/job.model'
import { JobPortals } from '@models/raw-job.model'
import { UpdateNaukriJob } from '../../services/jobs/update-naukari.service'

export default async function updateJobs() {
	try {
		// Fetch raw jobs where `isUpdated` is true
		const rawJobs = await App.Models.RawJob.find({ isUpdated: true, isDeleted: false }).limit(10)

		if (rawJobs.length) {
			Logger.info(`Found ${rawJobs.length} jobs for update.`)
			for (const rawJob of rawJobs) {
				const { rawData, portal } = rawJob
				let jobObj: Partial<I_Job>
				Logger.info(`Processing RawJob ID: ${rawJob.id} for portal: ${portal}`)
				// Handle portal-specific logic
				if (portal === JobPortals.Naukri) {
					Logger.info('Handling Naukri job update.')
					const updatedJobs = await UpdateNaukriJob(rawData)
					if (updatedJobs.isSuccess) {
						jobObj = {
							portal,
							...updatedJobs.data,
						}
						await App.Models.Job.findOneAndUpdate(
							{ id: rawData.id.toString() }, // Find job by ID
							jobObj, // Update object
							{
								new: true, // Return the updated document
								upsert: false, // Do not create a new document if none is found
							}
						)
						// Reset the `isUpdated` flag
						rawJob.isUpdated = false
						// Save the updated document
						await rawJob.save()
						Logger.info(`Updated RawJob ID: ${rawData.id} for portal: ${portal}`)
					}
				}
			}
		} else {
			Logger.info('No jobs found for update.')
		}
	} catch (error) {
		Logger.error(`Error updating raw job data: ${error?.message}`)
	}
}
