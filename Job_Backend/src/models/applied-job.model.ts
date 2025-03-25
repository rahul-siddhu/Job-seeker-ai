import '@core/declarations'
import { Schema, model as Model, Document } from 'mongoose'
import { Models } from '@core/constants/database-models'
const ObjectId = Schema.Types.ObjectId

export interface I_Applied_Job extends Document {
	_job: typeof ObjectId
	_user: typeof ObjectId
	appliedAt: Date
}

const schema = new Schema<I_Applied_Job>(
	{
		_job: { type: ObjectId, ref: Models.Job },
		_user: { type: ObjectId, ref: Models.User },
		appliedAt: Date,
	},
	{
		timestamps: true,
		versionKey: false,
	}
)

export const AppliedJobModel = Model<I_Applied_Job>(Models.AppliedJob, schema)
