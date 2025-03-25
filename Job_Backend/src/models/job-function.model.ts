import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

interface I_Job_Function {
	name: string
}
const schema = new Schema<I_Job_Function>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const JobFunctionModel = model(Models.JobFunction, schema)
