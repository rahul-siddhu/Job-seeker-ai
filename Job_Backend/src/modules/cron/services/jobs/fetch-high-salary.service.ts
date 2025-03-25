import databaseService from '@helpers/database-factory.helper'
import { Frequencies } from '@models/job.model'
import { Types } from 'mongoose'

export const sortFieldsOfFetchHighSalary = {
	key: ['normalizedMaxSalary'],
	object: {
		normalizedMaxSalary: 'normalizedMaxSalary',
	},
}

export default async function FetchHighSalary(data: any) {
	const { _designation } = data
	const query = []
	const matchObj = {
		'designation._id': Types.ObjectId.createFromHexString(_designation.toString()),
	}
	const jobCount = await App.Models.Job.countDocuments(matchObj)
	let top10PercentileLimit = Math.ceil(jobCount * 0.1)
	if (top10PercentileLimit < 1) top10PercentileLimit = 1
	// Match
	query.push(databaseService.aggregationMatch(matchObj))
	// Add Field
	query.push(
		databaseService.aggregationAddFields({
			// Calculate normalized min and max salaries to annual equivalent
			normalizedMinSalary: {
				$multiply: [
					{ $ifNull: ['$salary.min.amount', 0] },
					{
						$switch: {
							branches: [
								{
									case: { $eq: ['$salary.frequency', Frequencies.hourly] },
									then: 40 * 5 * 52,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.daily] },
									then: 5 * 52,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.monthly] },
									then: 12,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.annually] },
									then: 1,
								},
							],
							default: 0,
						},
					},
				],
			},
			normalizedMaxSalary: {
				$multiply: [
					{ $ifNull: ['$salary.max.amount', 0] },
					{
						$switch: {
							branches: [
								{
									case: { $eq: ['$salary.frequency', Frequencies.hourly] },
									then: 40 * 5 * 52,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.daily] },
									then: 5 * 52,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.monthly] },
									then: 12,
								},
								{
									case: { $eq: ['$salary.frequency', Frequencies.annually] },
									then: 1,
								},
							],
							default: 0,
						},
					},
				],
			},
			// avgSalary: { $avg: ['$normalizedMinSalary', '$normalizedMaxSalary'] }, // Calculate average of normalized salaries
		})
	)

	// Limit
	query.push(databaseService.aggregationLimit(top10PercentileLimit))

	query.push(
		databaseService.aggregationProject({
			salary: 1,
			normalizedMinSalary: 1,
			normalizedMaxSalary: 1,
			// avgSalary: 1,
		})
	)

	const sortObj: any = {
		[sortFieldsOfFetchHighSalary.object[sortFieldsOfFetchHighSalary.key[0]]]: -1,
	}
	query.push(databaseService.aggregationSort(sortObj))

	const jobs: any = await databaseService.aggregationQuery(App.Models.Job, query)

	// Get the last job in the array (the lowest salary in the top 10 percentile)
	const lastJob = jobs[jobs.length - 1]

	if (lastJob) {
		return lastJob
	} else {
		return null // If no jobs found
	}
}
