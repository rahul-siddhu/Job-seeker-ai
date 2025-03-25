import { Models } from '@core/constants/database-models'
import '@core/declarations'
import { model, Schema } from 'mongoose'

interface I_Skill {
	name: string
}
const schema = new Schema<I_Skill>(
	{
		name: String,
	},
	{ timestamps: true, versionKey: false }
)

export const SkillModel = model(Models.Skill, schema)
