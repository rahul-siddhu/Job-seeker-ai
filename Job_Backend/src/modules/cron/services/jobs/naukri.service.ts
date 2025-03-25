import { I_Job } from '@models/job.model'
import Company from './collections/company.service'
// import Designation from './collections/designation.service'
import { jobNumberIncrementer } from '@core/utils'
import ExtractTags from './extract-tags.service'
import ExtractWorkModel from './extract-work-model.service'
import { fetchExperienceLevels, parseCoordinates, parseLocation } from '@core/field-mapping'
import { ClearText } from './clear-text.service'

export default async function NaukriJob(rawData: any) {
	try {
		if (rawData) {
			// Location
			const location = await parseLocation(rawData.location)

			// Check if company exist or not. If not exist then create
			const companyResp = await Company({
				name: rawData.company.trim(),
				location,
			})
			// Check if designation exist or not. If not exist then create
			// const designationResp = await Designation({
			// 	name: rawData.designation.trim(),
			// })

			let experienceLevel: any = []
			if (rawData.experience && rawData.experience?.range) {
				experienceLevel = await fetchExperienceLevels(rawData.experience.range)
			}

			// Finalize the what should be job text to find the match score
			const jobText = `Job Detail: ${rawData.jobDetail?.text}. Job About: ${rawData.about?.text}. Job Types: ${rawData.jobType}. `

			let designationText = ''
			if (rawData.designation?.name && rawData.designation?.name != '')
				designationText += `${rawData.designation.name}. `

			const skillText =
				rawData.skills?.names && rawData.skills?.names?.length
					? `${rawData.skills?.names.join(' ')}`
					: ''

			// Find the Job tags
			const JobTags = await ExtractTags({
				text: jobText,
				applicants: rawData.applicants,
				postedAt: rawData.postedAt,
				companyRating: companyResp ? companyResp.rating : undefined,
			})

			// Finding Work model
			const workModel = ExtractWorkModel(jobText)

			const jobObj: Partial<I_Job> = {
				id: rawData.id.toString() || undefined,
				salary: rawData.salary || undefined,
				jobType: rawData.jobType || undefined,
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

				company: {
					_id: companyResp ? companyResp._id : undefined,
					name: companyResp.name,
				},
				designation: {
					// _id: designationResp ? designationResp._id : undefined,
					name: rawData.designation.trim(),
					// refName: designationResp ? designationResp.name : undefined,
				},
				industry: {
					name: rawData.industry.trim(),
				},
				jobFunction: {
					name: rawData.jobFunction.trim(),
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
