import constant from '@core/constants'
import { OpenaiHelper } from '@helpers/open-ai.helper'
import { Frequencies, JobTags } from '@models/job.model'
import { Batchfor, BatchStatuses } from '@models/open-ai-batch.model'
import { ClearText } from '@modules/cron/services/jobs/clear-text.service'
import FetchHighSalary from '@modules/cron/services/jobs/fetch-high-salary.service'

export const convertToAnnualSalary = (data: any) => {
	const { frequency } = data
	let { salary } = data
	if (salary && frequency) {
		if (frequency == Frequencies.hourly) {
			salary = salary.amount * 40 * 5 * 52
		} else if (frequency == Frequencies.daily) {
			salary = salary.amount * 5 * 52
		} else if (frequency == Frequencies.monthly) {
			salary = salary.amount * 12
		} else if (frequency == Frequencies.annually) {
			salary = salary.amount * 1
		} else {
			return null
		}
		return salary
	}
	return null
}

const addHighSalaryTag = async (data: any) => {
	const { _job, _designation, salary } = data
	// High Salary
	if (_designation && salary) {
		const highSalaryJob = await FetchHighSalary({ _designation })
		const maxSalaryOfJob = convertToAnnualSalary({
			salary: salary.max,
			frequency: salary.frequency,
		})
		if (highSalaryJob) {
			const maxSalary = highSalaryJob.normalizedMaxSalary
			if (maxSalaryOfJob && maxSalary) {
				if (maxSalaryOfJob > maxSalary) {
					const job = await App.Models.Job.findOne({
						_id: _job,
					})
					if (job) {
						const tags = job.tags
						tags.job.unshift(JobTags.HighSalary)
						job.tags = tags
						await job.save()
					}
				}
			}
		} else {
			if (maxSalaryOfJob > constant.HIGH_SALARY_MIN_SALARY) {
				const job = await App.Models.Job.findOne({
					_id: _job,
				})
				if (job) {
					const tags = job.tags
					tags.job.unshift(JobTags.HighSalary)
					job.tags = tags
					await job.save()
				}
			}
		}
	}
}

export default async function RetrieveJobBatch() {
	try {
		const openAiBatches = await App.Models.OpenAiBatch.find({
			for: Batchfor.Job,
			status: BatchStatuses.InProgress,
		})

		if (openAiBatches && openAiBatches.length) {
			for (let i = 0; i < openAiBatches.length; i++) {
				const openAiBatch = openAiBatches[i]
				const { batchId, jobNumbers } = openAiBatch

				const retrieveBatchResp = await OpenaiHelper.retrieveBatch(batchId)
				const { status } = retrieveBatchResp

				if (status === 'completed') {
					Logger.info(`Cron: Batch completed: ${batchId}`)
					const fileId = retrieveBatchResp.output_file_id

					if (fileId) {
						const retrieveFileResp = await OpenaiHelper.retrieveFileContent(fileId)
						const responseArray = retrieveFileResp.trim().split('\n')
						if (responseArray && responseArray.length) {
							for (let j = 0; j < responseArray.length; j++) {
								const responseObjString = responseArray[j]
								const responseObj = JSON.parse(responseObjString)

								if (responseObj.response.status_code == 200) {
									const jobObjString =
										responseObj.response.body.choices[0].message.content.trim()
									try {
										let jobObj = JSON.parse(jobObjString)
										let jobNumber = Number(jobObj['0'])
										// Sometimes GPT respond in "reponse" text
										if (!jobNumber || isNaN(jobNumber)) {
											jobObj = jobObj?.response
										}
										jobNumber = Number(jobObj['0'])
										// console.log('jobNumber:::', jobNumber)
										if (jobNumber && !isNaN(jobNumber)) {
											const industry = jobObj['1']
												? jobObj['1'].toString().trim()
												: ''
											const jobFunction = jobObj['2']
												? jobObj['2'].toString().trim()
												: ''
											const designation = jobObj['3']
												? jobObj['3'].toString().trim()
												: ''
											const skills = jobObj['4']
												? jobObj['4'].toString().trim().split(', ')
												: []
											const companyAbout = jobObj['5']
												? jobObj['5'].toString().trim()
												: ''

											const industryDoc = await App.Models.Industry.findOne({
												name: industry,
											})
											const jobFunctionDoc =
												await App.Models.JobFunction.findOne({
													name: jobFunction,
												})
											let designationDoc =
												await App.Models.Designation.findOne({
													name: designation,
												})
											if (!designationDoc) {
												designationDoc =
													await App.Models.Designation.create({
														name: designation,
													})
											}
											const jobDoc = await App.Models.Job.findOne({
												number: jobNumber,
											})
											if (jobDoc) {
												let isBatchFlag = true
												if (
													(industryDoc && !jobDoc.industry?.refName) ||
													jobDoc.industry?.refName == ''
												) {
													jobDoc.industry._id = industryDoc._id
													jobDoc.industry.refName = industryDoc.name
												} else {
													isBatchFlag = false
												}
												if (
													(jobFunctionDoc &&
														!jobDoc.jobFunction?.refName) ||
													jobDoc.jobFunction?.refName == ''
												) {
													jobDoc.jobFunction._id = jobFunctionDoc._id
													jobDoc.jobFunction.refName = jobFunctionDoc.name
												} else {
													isBatchFlag = false
												}
												if (
													(designationDoc &&
														!jobDoc.designation?.refName) ||
													jobDoc.designation?.refName === ''
												) {
													jobDoc.designation._id = designationDoc._id
													jobDoc.designation.refName = designationDoc.name
													jobDoc.vectorText.designation = await ClearText(
														designationDoc.name
													)

													// Extract High Salary tag
													await addHighSalaryTag({
														_job: jobDoc._id,
														_designation: jobDoc.designation._id,
														salary: jobDoc.salary,
													})
												} else {
													isBatchFlag = false
												}
												if (
													!jobDoc.skills?.names ||
													!jobDoc.skills?.names.length
												) {
													jobDoc.skills.names = skills
													jobDoc.vectorText.skill = await ClearText(
														skills.join(' ')
													)
												} else {
													isBatchFlag = false
												}
												if (
													!jobDoc.about?.text ||
													jobDoc.about?.text === ''
												) {
													jobDoc.about.text = companyAbout
												} else {
													isBatchFlag = false
												}

												if (isBatchFlag) {
													jobDoc.isBatched = true
												}
												await jobDoc.save()
											}
										}
									} catch (error) {
										Logger.error(error)
										continue
									}
								}
							}

							// Update the Open AI batch in db
							openAiBatch.status = BatchStatuses.Completed
							await openAiBatch.save()
						}
					} else {
						Logger.info(`Cron: Batch output file id not found: ${batchId}`)

						// Update the jobs isBatched false again
						await App.Models.Job.updateMany(
							{
								number: { $in: jobNumbers },
							},
							{
								$set: { isBatched: false },
							}
						)

						// Update the Open AI batch in db
						openAiBatch.status = BatchStatuses.Error
						await openAiBatch.save()
					}
				} else if (status == 'failed') {
					Logger.info(`Cron: Batch failed: ${batchId}`)

					// Update the jobs isBatched false again
					await App.Models.Job.updateMany(
						{
							number: { $in: jobNumbers },
						},
						{
							$set: { isBatched: false },
						}
					)

					// Update the Open AI batch in db
					openAiBatch.status = BatchStatuses.Failed
					await openAiBatch.save()
				}
			}
		}
	} catch (error) {
		Logger.error(error.message)
		return {
			isSuccess: false,
			error: error.message,
		}
	}
}
