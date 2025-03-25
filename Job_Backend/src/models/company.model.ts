import '@core/declarations'
import { Schema, model as Model } from 'mongoose'
import { Models } from '@core/constants/database-models'

const ObjectId = Schema.Types.ObjectId

export enum CompanyPortals {
	Glassdoor = 'Glassdoor',
	Crunchbase = 'Crunchbase',
	Ambitionbox = 'Ambitionbox',
}

export interface I_Company {
	id: string
	portal: CompanyPortals
	name: string
	offices: [
		{
			location: {
				area: string
				city: string
				state: string
				country: string
			}
		}
	]
	industry?: string
	description: {
		text: string
		html: string
	}
	url?: string
	website?: string
	logo?: string
	rating?: number
	reviewsCount?: number
	openings: number
	commitments: {
		_ids?: (typeof ObjectId)[]
		names: string[]
	}
	leadership: [
		{
			url: string
			logo: string
			name: string
			position: string
		}
	]
	companyInsight?: {
		financialInsight: {
			currentStage: string
			totalFunding: {
				value: number
				currency: string
			}
			revenue: {
				value: number
				currency: string
			}
			profitability: {
				value: number
				currency: string
			}
			expenses: {
				value: number
				currency: string
			}
			cashFlow: {
				value: number
				currency: string
			}
			earingsPerShare: {
				value: number
				currency: string
			}
			keyInvestors: string
		}
		gallery: string[]
		benefits: [
			{
				title: string
				description: string
			}
		]
	}
	isFeatured?: boolean
}

const schema = new Schema<I_Company>(
	{
		id: { type: String},
		portal: {
			type: String,
			enum: Object.values(CompanyPortals),
		},
		name: { type: String, required: true },
		offices: [
			{
				location: {
					area: String,
					city: String,
					state: String,
					country: String,
				},
			},
		],
		industry: String,
		description: {
			text: String,
			html: String,
		},
		url: String,
		website: String,
		logo: String,
		rating: { type: Number, default: 0 },
		reviewsCount: { type: Number, default: 0 },
		openings: { type: Number, default: 0 },
		commitments: {
			_ids: [{ type: ObjectId, ref: Models.Commitment }],
			names: [{ type: String }],
		},
		leadership: [
			{
				url: String,
				logo: String,
				name: String,
				position: String,
			},
		],
		companyInsight: {
			financialInsight: {
				currentStage: String,
				totalFunding: {
					value: Number,
					currency: String,
				},
				revenue: {
					value: Number,
					currency: String,
				},
				profitability: {
					value: Number,
					currency: String,
				},
				expenses: {
					value: Number,
					currency: String,
				},
				cashFlow: {
					value: Number,
					currency: String,
				},
				earingsPerShare: {
					value: Number,
					currency: String,
				},
				keyInvestors: String,
			},
			gallery: [String],
			benefits: [
				{
					title: String,
					description: String,
				},
			],
		},
		isFeatured: { type: Boolean, default: false },
	},
	{
		autoIndex: true,
		versionKey: false,
		timestamps: true,
	}
)

export const CompanyModel = Model<I_Company>(Models.Company, schema)
