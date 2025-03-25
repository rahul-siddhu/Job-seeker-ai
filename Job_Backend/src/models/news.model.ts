import { Models } from '@core/constants/database-models'
import { Schema, model as Model } from 'mongoose'
import { NewsPortals } from './raw-news.model'
const ObjectId = Schema.Types.ObjectId

interface IAuthor {
	name: string
	profile_link?: string
	designation?: string
}

interface ISource {
	name: string
	logo: string
}

export interface INews {
	id: string
	title: string
    portal: NewsPortals
	company: {
		_id: typeof ObjectId
		name: string
	},
	_category: typeof ObjectId
	description: {
		text: string
		html: string
	},
	keywords: string
	link: string
	author: IAuthor[]
	publicationDate: Date
	updatedDate?: Date
	source: ISource
	thumbnailUrl: string
	content: {
		text: string
		html: string
	},
	image?: string
	isTrending: boolean
}

const newsSchema = new Schema<INews>(
	{
		id: { type: String},
		company: { _id: { type: ObjectId, ref: Models.Company }, name: String },
		_category: { type: ObjectId, required: true, ref: Models.NewsCategory },
		title: { type: String, required: true },
		portal: {
			type: String,
			enum: Object.values(NewsPortals),
		},
		description: {
			text: String,
			html: String,
		},
		keywords: { type: String, required: true },
		link: { type: String, required: true },
		author: [
			{
				name: { type: String },
				profile_link: { type: String },
				designation: { type: String },
			},
		],
		publicationDate: { type: Date, required: true },
		updatedDate: { type: Date },
		isTrending: { type: Boolean, default: false },
		source: {
			name: { type: String, required: true },
			logo: { type: String, required: true },
		},
		thumbnailUrl: { type: String },
		content: {
			text: String,
			html: String,
		},
		image: { type: String },
	},
	{
		autoIndex: true,
		versionKey: false,
		timestamps: true, // Adds createdAt and updatedAt timestamps
	}
)

export const NewsModel = Model<INews>(Models.News, newsSchema)
