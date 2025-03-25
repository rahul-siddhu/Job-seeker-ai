import '@core/declarations'
import { Schema, model as Model, Document } from 'mongoose'
import { Models } from '@core/constants/database-models'
const ObjectId = Schema.Types.ObjectId

export enum JobPortals {
	Linkedin = 'Linkedin',
	Indeed = 'Indeed',
	Naukri = 'Naukri',
	Internshala = 'Internshala',
	Apna = 'Apna',
	Timesjobs = 'Timesjobs',
	Freshersworld = 'Freshersworld',
}
export enum Currencies {
	Inr = 'INR',
	Usd = 'USD',
	Eur = 'EUR',
	Aed = 'AED',
	Gbp = 'GBP',
}
export enum Frequencies {
	hourly = 'hourly',
	daily = 'daily',
	monthly = 'monthly',
	annually = 'annually',
}
export enum JobTypes {
	FullTime = 'Full time',
	PartTime = 'Part time',
	Internship = 'Internship',
	Contract = 'Contract',
	Freelance = 'Freelance',
}
export enum WorkModels {
	InOffice = 'In Office',
	FromHome = 'From Home',
	Hybrid = 'Hybrid',
}
export enum ExperienceLevels {
	InternLevel = 'Intern Level',
	EntryLevel = 'Entry Level',
	MidLevel = 'Mid Level',
	SeniorLevel = 'Senior Level',
	Director = 'Director',
	Executive = 'Executive',
}
export enum JobTags {
	HighSalary = 'High Salary',
	Rated4PlusStar = 'Rated 4+ Star',
	XColleaguesWorkHere = 'X Colleagues work here',
	FemalePreferred = 'Female Preferred',
	EarlyApplicant = 'Early Applicant',
	Remote = 'Remote',
}
export enum MatchTags {
	UrgentHiring = 'Urgent Hiring',
	WorkLifeBalance = 'Work-Life Balance',
	LeadershipRole = 'Leadership Role',
	GrowthOpportunities = 'Growth Opportunities',
}

export interface I_Job extends Document {
	portal: JobPortals
	company: {
		_id: typeof ObjectId
		name: string
	}
	designation?: {
		_id?: typeof ObjectId
		name?: string
		refName?: string
	}
	industry?: {
		_id?: typeof ObjectId
		name: string
		refName?: string
	}
	jobFunction?: {
		_id?: typeof ObjectId
		name: string
		refName?: string
	}
	skills: {
		_ids?: (typeof ObjectId)[]
		names: string[]
	}
	number: number
	id: string
	salary: {
		min: {
			amount: number
			currency: Currencies
		}
		max: {
			amount: number
			currency: Currencies
		}
		frequency: Frequencies
		description: string
	}
	location: {
		area?: string
		city: string
		state: string
		country: string
	}
	locationCoordinates: {
		type: string
		coordinates: number[]
	}
	postedAt: Date
	applyUrls: {
		jobUrl: string
		externalUrl: string
	}
	jobType: JobTypes[]
	workModel: WorkModels
	experience: {
		range: {
			from: number
			to: number
		}
		level: ExperienceLevels[]
	}
	postedBy: {
		url: string
		profileImage: string
		name: string
	}
	applicants: number
	about: {
		text: string
		html: string
	}
	jobDetail: {
		text: string
		html: string
	}
	qualification: {
		text: string
		html: string
	}
	tags: {
		job: string[]
		match: string[]
	}
	vectorText: {
		designation: string
		skill: string
	}
	isBlackListed: boolean
	isExpired: boolean
	isBatched: boolean
}

const JobSchema = new Schema<I_Job>(
	{
		company: { _id: { type: ObjectId, ref: Models.Company }, name: String },
		designation: {
			_id: { type: ObjectId, ref: Models.Designation },
			name: String,
			refName: String,
		},
		industry: { _id: { type: ObjectId, ref: Models.Industry }, name: String, refName: String },
		jobFunction: {
			_id: { type: ObjectId, ref: Models.JobFunction },
			name: String,
			refName: String,
		},
		skills: {
			_ids: [{ type: ObjectId }],
			names: [{ type: String }],
		},
		portal: {
			type: String,
			enum: Object.values(JobPortals),
		},
		number: {
			type: Number,
			unique: true,
			required: true,
		},
		id: String,
		salary: {
			min: {
				amount: Number,
				currency: {
					type: String,
					enum: Object.values(Currencies),
				},
			},
			max: {
				amount: Number,
				currency: {
					type: String,
					enum: Object.values(Currencies),
				},
			},
			frequency: {
				type: String,
				enum: Object.values(Frequencies),
			},
			description: String,
		},
		location: {
			area: String,
			city: String,
			state: String,
			country: String,
		},
		locationCoordinates: {
			type: {
				type: String,
			},
			coordinates: [Number],
		},
		postedAt: Date,
		applyUrls: {
			jobUrl: String,
			externalUrl: String,
		},
		jobType: {
			type: [String],
			enum: Object.values(JobTypes),
		},
		workModel: {
			type: String,
			enum: Object.values(WorkModels),
		},
		experience: {
			range: {
				from: Number,
				to: Number,
			},
			level: {
				type: [String],
				enum: Object.values(ExperienceLevels),
			},
		},
		postedBy: {
			url: String,
			profileImage: String,
			name: String,
		},
		applicants: { type: Number, default: 0 },
		about: {
			text: String,
			html: String,
		},
		jobDetail: {
			text: String,
			html: String,
		},
		qualification: {
			text: String,
			html: String,
		},
		tags: {
			job: {
				type: [String],
				enum: Object.values(JobTags),
			},
			match: {
				type: [String],
				enum: Object.values(MatchTags),
			},
		},
		vectorText: {
			designation: String,
			skill: String,
		},
		isBlackListed: {
			type: Boolean,
			default: false,
		},
		isExpired: {
			type: Boolean,
			default: false,
		},
		isBatched: {
			type: Boolean,
			default: false,
		},
	},
	{
		autoIndex: true,
		timestamps: true,
		versionKey: false,
	}
)

JobSchema.index({ locationCoordinates: '2dsphere' })

export const JobModel = Model<I_Job>(Models.Job, JobSchema)
