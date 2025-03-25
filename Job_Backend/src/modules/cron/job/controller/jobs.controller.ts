import '@core/declarations'
import { JobPortals } from '@models/raw-job.model'
import NaukriJob from '../../services/jobs/naukri.service'
import { I_Job } from '@models/job.model'
import IndeedJob from '@modules/cron/services/jobs/indeed.service'
import FreshersworldJob from '@modules/cron/services/jobs/freshersworld.service'
import ApnaJobs from '@modules/cron/services/jobs/apna.service'
import InternshalaJobs from '@modules/cron/services/jobs/internshala.service'
import TimesJobs from '@modules/cron/services/jobs/timesjobs.service'

// This controller is part of a cron job(cron process) that fetches jobs from various job portals and dumps them into the job collection
export default async function Jobs() {
	try {
		const rawJobs = await App.Models.RawJob.find({
			// portal: JobPortals.Apna,
			isDumped: false,
			isDeleted: false,
		}).limit(1000)
		if (rawJobs.length) {
			Logger.info('Cron: Raw data found for job')
			for (const rawJob of rawJobs) {
				const portal = rawJob.portal
				const rawData = rawJob.rawData
				let jobObj: Partial<I_Job>

				if (portal == JobPortals.Naukri) {
					const naukriJobResp = await NaukriJob(rawData)
					if (naukriJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...naukriJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': {
								$regex: jobObj.company.name.toString(),
								$options: 'i',
							},
							'designation.name': {
								$regex: jobObj.designation.name.toString(),
								$options: 'i',
							},
							'location.city': jobObj.location.city,
							// 'location.state': jobObj.location.state,
							// 'location.country': jobObj.location.country,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				} else if (portal == JobPortals.Freshersworld) {
					const freshersworldJobResp = await FreshersworldJob(rawData)
					if (freshersworldJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...freshersworldJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': {
								$regex: jobObj.company.name.toString(),
								$options: 'i',
							},
							'designation.name': {
								$regex: jobObj.designation.name.toString(),
								$options: 'i',
							},
							'location.city': jobObj.location.city,
							// 'location.state': jobObj.location.state,
							// 'location.country': jobObj.location.country,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				} else if (portal == JobPortals.Indeed) {
					const indeedJobResp = await IndeedJob(rawData)
					if (indeedJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...indeedJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': {
								$regex: jobObj.company.name.toString(),
								$options: 'i',
							},
							'designation.name': {
								$regex: jobObj.designation.name.toString(),
								$options: 'i',
							},
							'location.city': jobObj.location.city,
							// 'location.state': jobObj.location.state,
							// 'location.country': jobObj.location.country,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				} else if (portal == JobPortals.Apna) {
					// console.log('id::', rawData.id)
					const apnaJobResp = await ApnaJobs(rawData)

					if (apnaJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...apnaJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': jobObj.company.name,
							'designation.name': jobObj.designation.name,
							'location.city': jobObj.location.city,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				} else if (portal == JobPortals.Internshala) {
					// console.log('id::', rawData.id)
					const internshalaJobResp = await InternshalaJobs(rawData)
					if (internshalaJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...internshalaJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': jobObj.company?.name || undefined,
							'designation.name': jobObj.designation.name,
							'location.city': jobObj.location.city,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				} else if (portal == JobPortals.Timesjobs) {
					// console.log('id::', rawData.id)
					const TimesJobResp = await TimesJobs(rawData)
					if (TimesJobResp.isSuccess) {
						// Identify the job data is incomplete: Pending

						jobObj = {
							portal,
							...TimesJobResp.data,
						}
						// Check if job is already exist
						const oldJob = await App.Models.Job.findOne({
							'company.name': jobObj.company?.name || undefined,
							'designation.name': jobObj.designation.name,
							'location.city': jobObj.location.city,
							'experience.range.from': jobObj.experience.range.from,
							'experience.range.to': jobObj.experience.range.to,
						})
						if (oldJob) {
							delete jobObj.number
							// Update the job with new data
							await App.Models.Job.findByIdAndUpdate(oldJob._id, jobObj, {
								new: true,
							})
						} else {
							// Create a new job
							await App.Models.Job.create(jobObj)
						}
						Logger.info(`Job id: ${rawData.id} has been dumped in job collection`)
						// Update the flag in raw collection that data fetched
						rawJob.isDumped = true
						await rawJob.save()
					}
				}
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
