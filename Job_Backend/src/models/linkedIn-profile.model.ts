import { Schema, model as Model } from 'mongoose'
import { Models } from '@core/constants/database-models'

const ObjectId = Schema.Types.ObjectId

type file = {
  name: string
  key: string
  url: string
}
interface I_File {
  name?: string
  key?: string
  url?: string
  _id?: boolean
}

const fileSchema = new Schema<I_File>({
  name: String,
  key: String,
  url: String,
  _id: false,
})

export interface I_LinkedIn_Profile {
  _job: typeof ObjectId
  linkedInProfileData: {
    name: string
    profilePic: file
    profileUrl: string
  }[]
}

const schema = new Schema<I_LinkedIn_Profile>(
  {
    _job: { type: ObjectId, ref: Models.Job, required: true },
    linkedInProfileData: [
      {
        name: { type: String, required: true },
        profilePic: fileSchema,
        profileUrl: { type: String, required: true },
      },
    ],
  },
  {
    versionKey: false,
    timestamps: true,
  }
)

export const LinkedInProfileModel = Model<I_LinkedIn_Profile>(Models.LinkedInProfile, schema)
