import joi from 'joi'
import { JobPortals } from '@models/raw-job.model'
import { CompanyPortals } from '@models/raw-company.model'

export const RawJobsDTO = joi.object({
	portal: joi
		.string()
		.valid(...Object.values(JobPortals))
		.required(),
	jobPostedAt: joi.date().required(),
	rawData: joi.array().items(joi.any()).max(1000).required(),
})

export const RawCompaniesDTO = joi.object({
	portal: joi
		.string()
		.valid(...Object.values(CompanyPortals))
		.required(),
	rawData: joi.array().items(joi.any()).max(1000).required(),
})
