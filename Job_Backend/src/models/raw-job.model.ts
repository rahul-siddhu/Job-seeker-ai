import { Models } from '@core/constants/database-models'
import { Schema, model as Model } from 'mongoose'

export enum JobPortals {
	Linkedin = 'Linkedin',
	Indeed = 'Indeed',
	Naukri = 'Naukri',
	Internshala = 'Internshala',
	Apna = 'Apna',
	Timesjobs = 'Timesjobs',
	Freshersworld = 'Freshersworld',
}

export interface I_Raw_Job {
	portal: JobPortals
	jobPostedAt: Date
	isDumped: boolean
	isDeleted: boolean
	isUpdated: boolean
	rawData: object
}

const schema = new Schema<I_Raw_Job>(
	{
		portal: {
			type: String,
			enum: Object.keys(JobPortals),
		},
		jobPostedAt: Date,
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

export const RawJobModel = Model<I_Raw_Job>(Models.RawJob, schema)
