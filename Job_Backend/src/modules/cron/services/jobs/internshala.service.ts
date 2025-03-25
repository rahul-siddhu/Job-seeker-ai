import { Frequencies, I_Job, JobTypes, WorkModels } from '@models/job.model'
import Company from './collections/company.service'
// import Designation from './collections/designation.service'
// import Industry from './collections/industry.service'
// import JobFunction from './collections/job-function.service'
// import { OpenaiHelper } from '@helpers/open-ai.helper'
import { jobNumberIncrementer } from '@core/utils'
import ExtractTags from './extract-tags.service'
import ExtractWorkModel from './extract-work-model.service'
import { fetchExperienceLevels, parseCoordinates, parseLocation } from '@core/field-mapping'
import { ClearText } from './clear-text.service'

export default async function InternshalaJobs(rawData: any) {
	try {
		if (rawData) {
			// Location
			const location = await parseLocation(rawData.location)

			// Check if company exist or not. If not exist then create
			let company = undefined
			const companyResp = await Company({
				name: rawData.company?.trim() || undefined,
				location,
			})
			if (companyResp) {
				company = {
					_id: companyResp._id,
					name: companyResp.name,
				}
			}

			// Salary
			let salary = undefined
			if (rawData.salary) {
				salary = {
					min: {
						amount: rawData.salary.min?.amount || undefined,
						currency: rawData.salary.min?.currency?.trim() || undefined,
					},
					max: {
						amount: rawData.salary.max?.amount || undefined,
						currency: rawData.salary.max?.currency?.trim() || undefined,
					},
					frequency: rawData.salary?.frequency?.trim() || Frequencies.annually,
					description: rawData.salary?.description?.trim() || '',
				}
			}

			let experienceLevel: any = []
			if (rawData.experience && rawData.experience?.range) {
				experienceLevel = await fetchExperienceLevels(rawData.experience.range)
			}

			// Finalize the what should be job text to find the match score
			const jobText = `Job Detail: ${rawData.jobDetail?.text}. Job About: ${rawData.about?.text}. Job Types: ${rawData.jobType}. `

			let designationText = ''
			if (rawData.designation && rawData.designation != '')
				designationText += `${rawData.designation}. `

			const skillText =
				rawData.skills && rawData.skills.length ? `${rawData.skills.join(' ')}` : ''

			// Find the Job tags
			const JobTags = await ExtractTags({
				text: jobText,
				applicants: rawData.applicants,
				postedAt: rawData.postedAt,
				companyRating: companyResp ? companyResp.rating : undefined,
			})

			// Finding Work model
			let workModel = rawData.workModel
			if (!workModel || workModel == '') {
				workModel = ExtractWorkModel(jobText)
			} else if (!Object.values(WorkModels).includes(workModel)) {
				workModel = WorkModels.InOffice
			}
			// Job type
			let jobType = undefined
			if (rawData.jobType && Object.values(JobTypes).includes(rawData.jobType)) {
				jobType = rawData.jobType
			}

			const jobObj: Partial<I_Job> = {
				id: rawData.id.toString() || undefined,
				salary,
				jobType,
				location,
				locationCoordinates: rawData.location
					? await parseCoordinates(rawData.location)
					: undefined,
				applyUrls: rawData.applyUrls || undefined,
				postedAt: rawData.postedAt || undefined,
				experience: {
					range:
						rawData.experience && rawData.experience?.range
							? rawData.experience.range
							: undefined,
					level: experienceLevel,
				},
				postedBy: rawData.postedBy || undefined,
				applicants: Number(rawData.applicants) || undefined,
				about: rawData.about || undefined,
				jobDetail: rawData.jobDetail || undefined,
				qualification: rawData.qualification || undefined,
				isExpired: rawData.isExpired || undefined,

				company,
				designation: {
					// _id: designationResp ? designationResp._id : undefined,
					name: rawData.designation.trim(),
					// refName: designationResp ? designationResp.name : undefined,
				},
				industry: {
					// _id: industryResp ? industryResp._id : undefined,
					name: rawData.industry.trim(),
					// refName: industryResp ? industryResp.name : undefined,
				},
				jobFunction: {
					// _id: jobFunctionResp ? jobFunctionResp._id : undefined,
					name: rawData.jobFunction.trim(),
					// refName: jobFunctionResp ? jobFunctionResp.name : undefined,
				},
				skills: {
					// _ids: skillResp && skillResp.length ? skillResp : [],
					names: rawData.skills && rawData.skills.length ? rawData.skills : [],
				},
				number: await jobNumberIncrementer(),
				tags: JobTags,
				workModel,
				vectorText: {
					designation: await ClearText(designationText),
					skill: await ClearText(skillText),
				},
			}
			return {
				isSuccess: true,
				data: jobObj,
			}
		}
	} catch (error) {
		Logger.error(error)
		return {
			isSuccess: false,
		}
	}
}
