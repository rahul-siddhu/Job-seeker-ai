import '@core/declarations'
import { Schema, model as Model, Document } from 'mongoose'
import { Models } from '@core/constants/database-models'
const ObjectId = Schema.Types.ObjectId

export interface I_Job_Match_Reason extends Document {
	_job: typeof ObjectId
	_user: typeof ObjectId
	reason: string
}

const schema = new Schema<I_Job_Match_Reason>(
	{
		_job: { type: ObjectId, ref: Models.Job },
		_user: { type: ObjectId, ref: Models.User },
		reason: String,
	},
	{
		timestamps: true,
		versionKey: false,
	}
)

export const JobMatchReasonModel = Model<I_Job_Match_Reason>(Models.JobMatchReason, schema)
