import { Models } from '@core/constants/database-models'
import { Schema, model as Model } from 'mongoose'

export enum NewsPortals {
    BusinessStandard= 'BusinessStandard',
    GoogleNews = 'GoogleNews',
    EconomicTimes = 'EconomicTimes',
}

export interface I_Raw_News extends Document {
	portal: NewsPortals
	isDumped: boolean
	isDeleted: boolean
	isUpdated: boolean
	rawData: object
}

const schema = new Schema<I_Raw_News>(
	{
		portal: {
			type: String,
			enum: Object.values(NewsPortals),
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

export const RawNewsModel = Model<I_Raw_News>(Models.RawNews, schema)