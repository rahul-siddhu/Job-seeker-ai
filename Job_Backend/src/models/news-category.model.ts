import '@core/declarations'
import { Models } from '@core/constants/database-models'
import { model, Schema } from 'mongoose'

interface I_NewsCategory {
	name: string
}
const schema = new Schema<I_NewsCategory>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const NewsCategoryModel = model<I_NewsCategory>(Models.NewsCategory, schema)