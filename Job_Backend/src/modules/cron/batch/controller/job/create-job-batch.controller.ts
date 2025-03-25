import '@core/declarations'
import moment from 'moment'
import constant from '@core/constants'
import { OpenaiHelper } from '@helpers/open-ai.helper'
import { Batchfor, BatchStatuses } from '@models/open-ai-batch.model'
import { JobPortals } from '@models/raw-job.model'
import { getFirstWords } from '@core/utils'

export default async function CreateJobBatch() {
	try {
		const jobs = await App.Models.Job.find({
			// portal: JobPortals.Internshala,
			$or: [
				{ 'industry.refName': { $exists: false } },
				{ 'jobFunction.refName': { $exists: false } },
				{ 'designation.refName': { $exists: false } },
				{ 'skills.names': [] },
				{ 'about.text': { $exists: false } },
				{ 'about.text': '' },
			],
			isBatched: false,
		}).limit(100)
		if (jobs && jobs.length) {
			Logger.info('Cron: Jobs found for Batch')

			const industries = await App.Models.Industry.find().lean()
			const jobFunctions = await App.Models.JobFunction.find().lean()

			const industryNames = industries.map((industry: any) => industry.name)
			const jobFunctionNames = jobFunctions.map((jobFunction: any) => jobFunction.name)
			const tasks = []
			const unixTimestamp = moment().valueOf().toString()
			const jobNumbers = jobs.map((job: any) => Number(job.number))

			for (let i = 0; i < jobs.length; i++) {
				const job = jobs[i]

				const industry = job.industry?.name || ''
				const jobFunction = job.jobFunction?.name || ''
				const designation = job.designation?.name || ''
				const company = job.company?.name || ''
				const jobDetail = job.jobDetail?.text ? getFirstWords(job.jobDetail.text, 100) : ''

				const prompt = `
						You are a classification assistant. 
						I will provide you with an input industry name, Job Function name, Job Title name, Company name and a predefined list of industries, Job Functions, Job Skills. 
						If industry and job function is empty then take whole inputs and find the industry and job function from the given list.
						Your task is to find followings,
						- Industry from the predefined list
						- Job function from the predefined list 
						- Extract the valid designation mentioned in the Input Job Title 
						- Find company about from the company name 
						- Find the skills of the job
						that best matches or describes the input industry, job function and designation. 
						If no exact match is found, select the closest match based on relevance or similarity.

						job number: ${job.number}

						Predefined Industry List:
						${JSON.stringify(industryNames)}
	
						Input Industry Name:
						${industry}
	
						Predefined Job Function List:
						${JSON.stringify(jobFunctionNames)}
	
						Input Job Function Name:
						${jobFunction}

						Input Job Title:
						${designation}

						Input Company Name:
						${company}

						Input Job Detail:
						${jobDetail}

						Response:
						Provide the best-matching industry from the predefined list.
						Respond with a JSON array where:
						- Index 0 should be same job number I provided
						- Index 1 is the best-matching industry
						- Index 2 is the best-matching job function
						- Index 3 is the designation
						- Index 4 is the job skills. It should be in comma seperated string. Do not add "skills" word at end of every skills. It should be exact name of skill.
						- Index 5 is the about of the company. it should be in 100 words.
					  `

				const task = {
					custom_id: `custom_${i}_${unixTimestamp}`,
					method: 'POST',
					url: '/v1/chat/completions',
					body: {
						model: constant.OPENAI.MODELS.GPT_40_MINI,
						temperature: 0.1,
						response_format: {
							type: 'json_object',
						},
						messages: [
							{
								role: 'user',
								content: prompt,
							},
						],
					},
				}

				tasks.push(task)
			}

			const batchJobResp = await OpenaiHelper.createBatch(tasks)
			if (batchJobResp) {
				// Update the jobs isBatched true
				await App.Models.Job.updateMany(
					{
						number: { $in: jobNumbers },
					},
					{
						$set: { isBatched: true },
					}
				)

				// Create a batch in db
				await App.Models.OpenAiBatch.create({
					batchId: batchJobResp.batchId,
					fileId: batchJobResp.fileId,
					for: Batchfor.Job,
					status: BatchStatuses.InProgress,
					jobNumbers,
				})
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
