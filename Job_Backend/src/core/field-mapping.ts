import '@core/declarations'
import constant from './constants'
import { ExperienceLevels, Frequencies } from '@models/job.model'
import { OlaMapsHelper } from '@helpers/ola-maps.helper'
import { UploadJobsDataToS3 } from '@modules/cron/services/jobs/upload-jobs-data.service'
import databaseService from '@helpers/database-factory.helper'

export function parseSalary(description: string) {
	const patterns = constant.REGEX.SALARY.PATTERNS

	// Initialize result
	const salary = {
		min: null,
		max: null,
		frequency: null,
		description: description,
	}

	// Try to match each pattern
	for (const [frequency, pattern] of Object.entries(patterns)) {
		const match = description.match(pattern)
		if (match) {
			if (frequency === 'HOURLY') {
				salary.min = { amount: parseInt(match[1].replace(/,/g, '')), currency: 'INR' }
				salary.frequency = Frequencies.hourly
				return salary
			}

			if (frequency === 'DAILY') {
				salary.min = { amount: parseInt(match[1].replace(/,/g, '')), currency: 'INR' }
				salary.frequency = Frequencies.daily
				return salary
			}

			if (frequency === 'MONTHLY_RANGE') {
				salary.min = { amount: parseInt(match[1] + (match[2] || '')), currency: 'INR' }
				salary.max = { amount: parseInt(match[3] + (match[4] || '')), currency: 'INR' }
				salary.frequency = Frequencies.monthly
				return salary
			}

			if (frequency === 'MONTHLY_MIN') {
				salary.min = { amount: parseInt(match[1] + (match[2] || '')), currency: 'INR' }
				salary.frequency = Frequencies.monthly
				return salary
			}

			if (frequency === 'ANNUAL_RANGE') {
				salary.min = { amount: parseInt(match[1] + (match[2] || '')), currency: 'INR' }
				salary.max = { amount: parseInt(match[3] + (match[4] || '')), currency: 'INR' }
				salary.frequency = Frequencies.annually
				return salary
			}

			if (frequency === 'ANNUAL_MAX') {
				salary.max = { amount: parseInt(match[1] + (match[2] || '')), currency: 'INR' }
				salary.frequency = Frequencies.annually
				return salary
			}
		}
	}

	// If no match is found, return null or handle as needed
	return null
}

export const parseLocation = async (location: any) => {
	const { area, city } = location
	let { state, country } = location

	if (city && (!state || !country)) {
		if (!state) {
			const cityDoc = await App.Models.City.findOne({
				name: databaseService.exactCaseInsensitiveSearchObj(city),
			}).populate('_state')
			if (cityDoc) {
				state = cityDoc._state.name
			}
		}
		if (!country) {
			const stateDoc = await App.Models.State.findOne({
				name: databaseService.exactCaseInsensitiveSearchObj(state),
			}).populate('_country')
			if (stateDoc) {
				country = stateDoc._country.name
			}
		}
	}
	return { area, city, state, country }
}

export const parseCoordinates = async (location: any) => {
	const { area, city, state, country } = location
	let address = ''
	let coordinates = undefined

	// Check the latlong exist in database
	const cityDoc = await App.Models.City.findOne({
		name: databaseService.exactCaseInsensitiveSearchObj(city),
	})
	if (cityDoc && cityDoc.coordinates?.lat && cityDoc.coordinates?.long) {
		coordinates = {
			type: constant.COORDINATES_TYPE,
			coordinates: [cityDoc.coordinates.long, cityDoc.coordinates.lat],
		}
	} else {
		if (area) {
			address += area
		}
		if (city) {
			address += address ? `, ${city}` : city
		}
		if (state) {
			address += address ? `, ${state}` : state
		}
		if (country) {
			address += address ? `, ${country}` : country
		}
		if (address != '') {
			const latLong = await OlaMapsHelper.getLatLong(address)
			if (latLong) {
				coordinates = {
					type: constant.COORDINATES_TYPE,
					coordinates: [latLong.long, latLong.lat],
				}

				// Store the lat long in database
				if (cityDoc) {
					cityDoc.coordinates = latLong
					await cityDoc.save()
				}
			}
		}
	}
	return coordinates
}

const experienceRanges = [
	{ level: ExperienceLevels.InternLevel, from: 0, to: 1 },
	{ level: ExperienceLevels.EntryLevel, from: 1, to: 2 },
	{ level: ExperienceLevels.MidLevel, from: 3, to: 6 },
	{ level: ExperienceLevels.SeniorLevel, from: 7, to: 12 },
	{ level: ExperienceLevels.Director, from: 12, to: 18 },
	{ level: ExperienceLevels.Executive, from: 18, to: Infinity },
]

export const fetchExperienceLevels = async (range: {
	from?: [number, string]
	to?: [number, string]
}) => {
	const from = Number(range.from)
	const to = Number(range.to)
	return experienceRanges
		.filter((experienceRange) => {
			// Handle optional `from` and `to`
			const isWithinLowerBound = from === undefined || experienceRange.to >= from
			const isWithinUpperBound = to === undefined || experienceRange.from <= to

			return isWithinLowerBound && isWithinUpperBound
		})
		.map((experienceRange) => experienceRange.level) // Map to the corresponding levels
}

export const deleteAllRelatedJobs = async (_job: any) => {
	const { isSuccess, error } = await UploadJobsDataToS3(_job)
	if (isSuccess) {
		await Promise.all([
			App.Models.AppliedJob.deleteMany({ _job }),
			App.Models.JobMatchReason.deleteMany({ _job }),
			App.Models.NotInterestedJob.deleteMany({ _job }),
			App.Models.ReportJob.deleteMany({ _job }),
			App.Models.SavedJob.deleteMany({ _job }),
			App.Models.Job.deleteOne({ _id: _job }),
		])
	}
	Logger.error(error)
}
