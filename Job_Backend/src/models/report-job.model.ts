import '@core/declarations'
import { Schema, model as Model, Document } from 'mongoose'
import { Models } from '@core/constants/database-models'
const ObjectId = Schema.Types.ObjectId

export interface I_Report_Job extends Document {
	_reportType: typeof ObjectId
	_job: typeof ObjectId
	_user: typeof ObjectId
	message: string
}

const schema = new Schema<I_Report_Job>(
	{
		_reportType: { type: ObjectId, ref: Models.ReportType },
		_job: { type: ObjectId, ref: Models.Job },
		_user: { type: ObjectId, ref: Models.User },
		message: String,
	},
	{
		timestamps: true,
		versionKey: false,
	}
)

export const ReportJobModel = Model<I_Report_Job>(Models.ReportJob, schema)
