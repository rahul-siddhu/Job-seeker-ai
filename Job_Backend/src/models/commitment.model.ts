import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

interface I_Commitment {
	name: string
}
const schema = new Schema<I_Commitment>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const CommitmentModel = model(Models.Commitment, schema)
