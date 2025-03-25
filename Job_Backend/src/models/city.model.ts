import { Schema, model as Model } from 'mongoose'
import { Models } from '@core/constants/database-models'

export interface I_City {
	_state: Schema.Types.ObjectId
	name: string
	isoCode: string
	coordinates: {
		lat: number
		long: number
	}
}

const schema = new Schema<I_City>(
	{
		_state: { type: Schema.Types.ObjectId, ref: Models.State, required: true },
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

export const CityModel = Model<I_City>(Models.City, schema)
