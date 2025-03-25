import { JobTags, MatchTags } from '@models/job.model'
// import FetchHighSalary from './fetch-high-salary.service'
// import constant from '@core/constants'

const tagRegex = (data: any) => {
	return new RegExp(`\\b(${data.join('|')})\\b`, 'gi')
}
// export const convertToAnnualSalary = (data: any) => {
// 	const { frequency } = data
// 	let { salary } = data
// 	if (salary && frequency) {
// 		if (frequency == Frequencies.hourly) {
// 			salary = salary.amount * 40 * 5 * 52
// 		} else if (frequency == Frequencies.daily) {
// 			salary = salary.amount * 5 * 52
// 		} else if (frequency == Frequencies.monthly) {
// 			salary = salary.amount * 12
// 		} else if (frequency == Frequencies.annually) {
// 			salary = salary.amount * 1
// 		} else {
// 			return null
// 		}
// 		return salary
// 	}
// 	return null
// }
export default async function ExtractTags(data: any) {
	const tags = {
		job: [],
		match: [],
	}
	if (data) {
		const { text, applicants, postedAt, companyRating } = data
		const now = new Date()
		const femalePreferredArr = ['female preferred']
		const urgentHiringArr = ['urgent', 'immediate start', 'immediate hire']
		const remoteArr = ['remote', 'work from home', 'WFH', 'hybrid']
		const workLifeBalanceArr = [
			'work-life balance',
			'work life balance',
			'flexible schedule',
			'well-being',
		]
		const leadershipRoleArr = ['manager', 'lead', 'director', 'head']
		const growthOpportunitiesArr = [
			'career advancement',
			'promotion',
			'learning',
			'development',
		]

		// High Salary
		// if (designation && salary) {
		// 	const highSalaryJob = await FetchHighSalary({ designation })
		// 	const maxSalaryOfJob = convertToAnnualSalary({
		// 		salary: salary.max,
		// 		frequency: salary.frequency,
		// 	})
		// 	if (highSalaryJob) {
		// 		const maxSalary = highSalaryJob.normalizedMaxSalary
		// 		if (maxSalaryOfJob && maxSalary) {
		// 			if (maxSalaryOfJob > maxSalary) {
		// 				tags.job.push(JobTags.HighSalary)
		// 			}
		// 		}
		// 	} else {
		// 		if (maxSalaryOfJob > constant.HIGH_SALARY_MIN_SALARY) {
		// 			tags.job.push(JobTags.HighSalary)
		// 		}
		// 	}
		// }

		// Rated 4+ Star
		if (companyRating && companyRating > 4) {
			tags.job.push(JobTags.Rated4PlusStar)
		}

		// Female Prefered
		const femalePreferredReg = tagRegex(femalePreferredArr)
		if (femalePreferredReg.test(text)) tags.job.push(JobTags.FemalePreferred)

		// Early Applicant
		if (applicants && postedAt) {
			const lastDateOfEarlyApplicant = new Date(now)
			lastDateOfEarlyApplicant.setDate(now.getDate() - 7)
			if (Number(applicants) <= 20 && lastDateOfEarlyApplicant < postedAt) {
				tags.job.push(JobTags.EarlyApplicant)
			}
		}

		// Urgent Hiring
		const urgentHiringReg = tagRegex(urgentHiringArr)
		if (urgentHiringReg.test(text)) tags.match.push(MatchTags.UrgentHiring)

		// Remote
		const remoteReg = tagRegex(remoteArr)
		if (remoteReg.test(text)) tags.job.push(JobTags.Remote)

		// work-Life Balance
		const workLifeBalanceReg = tagRegex(workLifeBalanceArr)
		if (workLifeBalanceReg.test(text)) tags.match.push(MatchTags.WorkLifeBalance)

		// Leadership Role
		const leadershipRoleReg = tagRegex(leadershipRoleArr)
		if (leadershipRoleReg.test(text)) tags.match.push(MatchTags.LeadershipRole)

		// Growth Opportunity
		const growthOpportunitiesReg = tagRegex(growthOpportunitiesArr)
		if (growthOpportunitiesReg.test(text)) tags.match.push(MatchTags.GrowthOpportunities)
	}
	return tags
}
