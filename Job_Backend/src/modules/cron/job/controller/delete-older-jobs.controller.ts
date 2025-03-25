import '@core/declarations'
import { deleteAllRelatedJobs } from '@core/field-mapping'
import moment from 'moment'

export default async function deleteOlderJobs() {
    try {
		// Calculate the date 30 days ago
		const thirtyDaysAgo = moment().subtract(30, 'days').toDate()
		// Query jobs posted more than 30 days ago
		const olderJobs = await App.Models.Job.find({
			postedAt: { $lt: thirtyDaysAgo },
        })
        if (olderJobs.length) {
            for (const job of olderJobs) {
                const _job = job._id.toString()
                Logger.info(`Deleted older job id : ${ _job}`)
                await deleteAllRelatedJobs(_job)
            }
        }
	} catch (error) {
        Logger.error(error?.message)
    }
}
