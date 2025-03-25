import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

interface I_Designation {
	name: string
}
const schema = new Schema<I_Designation>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const DesignationModel = model(Models.Designation, schema)
