import '@core/declarations'
import moment from 'moment'
import constant from '@core/constants'
import { OpenaiHelper } from '@helpers/open-ai.helper'
import { Batchfor, BatchStatuses } from '@models/open-ai-batch.model'
import { JobPortals } from '@models/raw-job.model'
import { getFirstWords } from '@core/utils'

export default async function CreateCompanyBatch() {
	try {
		const companies = await App.Models.Company.find({
			isBatched: false,
		}).limit(500)

		if (companies && companies.length) {
			Logger.info('Batch: Companies')

			const tasks = []
			const unixTimestamp = moment().valueOf().toString()
			const _companies = companies.map((company: any) => company._id.toString())

			for (let i = 0; i < companies.length; i++) {
				const company = companies[i]

				const _company = company._id.toString()
				const companyName = company.name

				const prompt = `
						You are a classification assistant. 
						I will provide you with an input company name. 
                        
                        Company id: ${_company}

						Company name: ${companyName}
                        
						Your task is to find followings for company,
                        Company Details,
                        - Company URL
                        - Founded In: It should be in year
                        - Size: Only provide the number of employees
                        - Headquarter
                        - Type 
                        - Industry
                        - Company Details (About)
                        - Company Rating: It should be number out of 5
                        - Company Reviews along with Categories with Percentage: It should be array of object. percentage should be out of 100
                        - Employee Reviews (8 count and it should be mix reviews like positive and negative ones)
                        - Leadership 

                        Financial Insights,
                        - Current Stage
                        - Expenses: It should be a number with currency
                        - Total Funding: It should be a number with currency
                        - Cash Flow: It should be a number with currency
                        - Revenue: It should be a number with currency
                        - Earnings per share: It should be a number with currency
                        - Profitability: It should be a number with currency
                        - Key Investors
                        - Current Openings: It should be a number 
                        - Company Image: It should be an array of image urls
                        - Company Benefits: It should be with categories with bullet points. Max 6 categories.
                        - Recent news from Company

						Response:
						Respond with a JSON array where:
						- Index 0 should be same Company id I provided
						- Index 1 should be same Company name I provided
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
						number: { $in: _companies },
					},
					{
						$set: { isBatched: true },
					}
				)

				// Create a batch in db
				await App.Models.OpenAiBatch.create({
					batchId: batchJobResp.batchId,
					fileId: batchJobResp.fileId,
					for: Batchfor.Company,
					status: BatchStatuses.InProgress,
					// jobNumbers,
				})
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
