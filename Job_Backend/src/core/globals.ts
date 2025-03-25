import Config, { ConfigInterface } from '@config'
import { Logger } from './logger'
import { GenerateCallableMessages } from './utils'
import path from 'path'
import _ from 'lodash'
const config: ConfigInterface = Config()

import { Messages } from '../response-messages'

// Database Models
import { RawJobModel } from '@models/raw-job.model'
import { RawCompanyModel } from '@models/raw-company.model'
import { JobModel } from '@models/job.model'
import { CompanyModel } from '@models/company.model'
import { RawNewsModel } from '@models/raw-news.model'
import { NewsCategoryModel } from '@models/news-category.model'
import { NewsModel } from '@models/news.model'
import { DesignationModel } from '@models/designation.model'
import { IndustryModel } from '@models/industry.model'
import { JobFunctionModel } from '@models/job-function.model'
import { CommitmentModel } from '@models/commitment.model'
import { SkillModel } from '@models/skill.model'
import { CityModel } from '@models/city.model'
import { StateModel } from '@models/state.model'
import { CountryModel } from '@models/country.model'
import { AppliedJobModel } from '@models/applied-job.model'
import { JobMatchReasonModel } from '@models/job-match-reason.model'
import { NotInterestedJobModel } from '@models/not-interested-job.model'
import { ReportJobModel } from '@models/report-job.model'
import { SavedJobModel } from '@models/saved-job.model'
import { LinkedInProfileModel } from '@models/linkedIn-profile.model'
import { OpenAiBatchModel } from '@models/open-ai-batch.model'

// Export Global Variables
export const Global: any = global
Global._ = _
Global.Logger = Logger
Global.App = {
	EXTENSION_ECOSYSTEM: path.extname(__filename) === '.js' ? 'js' : 'ts',
	Http: {
		app: null,
	},
	Config: config,
	Messages: GenerateCallableMessages(Messages),
	Models: {
		RawJob: RawJobModel,
		RawCompany: RawCompanyModel,
		Job: JobModel,
		Company: CompanyModel,
		RawNews: RawNewsModel,
		NewsCategory: NewsCategoryModel,
		News: NewsModel,
		Designation: DesignationModel,
		Industry: IndustryModel,
		JobFunction: JobFunctionModel,
		Commitment: CommitmentModel,
		Skill: SkillModel,
		City: CityModel,
		State: StateModel,
		Country: CountryModel,
		AppliedJob: AppliedJobModel,
		JobMatchReason: JobMatchReasonModel,
		NotInterestedJob: NotInterestedJobModel,
		ReportJob: ReportJobModel,
		SavedJob: SavedJobModel,
		LinkedInProfile : LinkedInProfileModel,
		OpenAiBatch: OpenAiBatchModel,
	},
}
