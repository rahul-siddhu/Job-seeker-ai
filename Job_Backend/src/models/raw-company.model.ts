import { Models } from '@core/constants/database-models'
import { Schema, model as Model } from 'mongoose'

export enum CompanyPortals {
	Glassdoor = 'Glassdoor',
	Crunchbase = 'Crunchbase',
	Ambitionbox = 'Ambitionbox',
}

export interface I_Raw_Company {
	portal: CompanyPortals
	isDumped: boolean
	isDeleted: boolean
	isUpdated: boolean
	rawData: object
}

const schema = new Schema<I_Raw_Company>(
	{
		portal: {
			type: String,
			enum: Object.keys(CompanyPortals),
		},
		isDumped: {
			type: Boolean,
			default: false,
		},
		isDeleted: {
			type: Boolean,
			default: false,
		},
		isUpdated: {
			type: Boolean,
			default: false,
		},
		rawData: Object,
	},
	{
		autoIndex: true,
		versionKey: false,
		timestamps: true,
	}
)

export const RawCompanyModel = Model<I_Raw_Company>(Models.RawCompany, schema)
