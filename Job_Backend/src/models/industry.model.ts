import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

interface I_Industry {
	name: string
}
const schema = new Schema<I_Industry>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const IndustryModel = model(Models.Industry, schema)
