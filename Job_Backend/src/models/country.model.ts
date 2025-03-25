import { Schema, model as Model } from 'mongoose'
import { Models } from '@core/constants/database-models'

export interface I_Country {
	name: string
	isoCode: string
	coordinates: {
		lat: number
		long: number
	}
}

const countrySchema = new Schema<I_Country>(
	{
		name: { type: String, required: true },
		isoCode: { type: String, required: true },
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

export const CountryModel = Model<I_Country>(Models.Country, countrySchema)
