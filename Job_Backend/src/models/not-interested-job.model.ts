import '@core/declarations'
import { Schema, model as Model, Document } from 'mongoose'
import { Models } from '@core/constants/database-models'
const ObjectId = Schema.Types.ObjectId

export interface I_Not_Interested_Job extends Document {
	_job: typeof ObjectId
	_user: typeof ObjectId
}

const schema = new Schema<I_Not_Interested_Job>(
	{
		_job: { type: ObjectId, ref: Models.Job },
		_user: { type: ObjectId, ref: Models.User },
	},
	{
		timestamps: true,
		versionKey: false,
	}
)

export const NotInterestedJobModel = Model<I_Not_Interested_Job>(Models.NotInterestedJob, schema)
