import { Schema, model as Model } from 'mongoose'
import { Models } from '@core/constants/database-models'

export interface I_State {
	_country: Schema.Types.ObjectId
	name: string
	isoCode: string
	coordinates: {
		lat: number
		long: number
	}
}

const stateSchema = new Schema<I_State>(
	{
		_country: { type: Schema.Types.ObjectId, ref: Models.Country, required: true },
		name: { type: String, required: true },
		isoCode: { type: String, required: false },
		coordinates: {
			lat: Number,
			long: Number,
		},
	},
	{
		versionKey: false,
		timestamps: true,
	}
)

export const StateModel = Model<I_State>(Models.State, stateSchema)
