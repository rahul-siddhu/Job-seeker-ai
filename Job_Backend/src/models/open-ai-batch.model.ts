import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

export enum BatchStatuses {
	Pending = 'Pending',
	InProgress = 'InProgress',
	Completed = 'Completed',
	Failed = 'Failed',
	Error = 'Error',
}
export enum Batchfor {
	Job = 'Job',
	Company = 'Company',
}

interface I_Open_Ai_Batch {
	batchId: string
	fileId: string
	for: Batchfor
	status: BatchStatuses
	jobNumbers: number[]
}
const schema = new Schema<I_Open_Ai_Batch>(
	{
		batchId: String,
		fileId: String,
		for: {
			type: String,
			enum: Batchfor,
		},
		status: {
			type: String,
			enum: Object.values(BatchStatuses),
		},
		jobNumbers: [Number],
	},
	{ timestamps: true, versionKey: false }
)

export const OpenAiBatchModel = model(Models.OpenAiBatch, schema)
