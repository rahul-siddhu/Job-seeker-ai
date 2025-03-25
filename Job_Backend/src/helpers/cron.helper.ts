import '@core/declarations'
import cron from 'node-cron'
import Jobs from '@modules/cron/job/controller/jobs.controller'
import Companies from '@modules/cron/company/controller/company.controller'
import CreateJobBatch from '@modules/cron/batch/controller/job/create-job-batch.controller'
import RetrieveJobBatch from '@modules/cron/batch/controller/job/retrieve-job-batch.controller'

class CronHelper {
	async cronJob(): Promise<void> {
		try {
			// Every hour
			let scrapRunning = false
			cron.schedule('* * * * *', async () => {
				Logger.info('cron run..')
				if (!scrapRunning) {
					scrapRunning = true
					await Companies()
					await Jobs()
					scrapRunning = false
				}
			})
			let createBatchRunning = false
			cron.schedule('* * * * *', async () => {
				Logger.info('cron run for create Batch..')
				if (!createBatchRunning) {
					createBatchRunning = true
					await CreateJobBatch()
					createBatchRunning = false
				}
			})
			let retrieveBatchRunning = false
			cron.schedule('* * * * *', async () => {
				Logger.info('cron run for retrieve Batch..')
				if (!retrieveBatchRunning) {
					retrieveBatchRunning = true
					await RetrieveJobBatch()
					retrieveBatchRunning = false
				}
			})
		} catch (error) {
			Logger.error(error?.message)
		}
	}
}
export default new CronHelper()
