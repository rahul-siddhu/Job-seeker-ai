const constant = {
	// COMMON
	DEVELOPMENT: 'development',
	X_POWERED_BY: 'x-powered-by',
	PORT: 5000,
	API_VERSION: '/api/v1',
	HIGH_SALARY_MIN_SALARY: 1200000,
	REGEX: {
		HTML_TO_TEXT: /<[^>]*>/g,
		SALARY: {
			PATTERNS: {
				HOURLY: /₹(\d+)\s+an\s+hour/,
				DAILY: /₹(\d+)\s+a\s+day/,
				MONTHLY_RANGE: /₹(\d+)(?:,(\d+))?\s*-\s*₹(\d+)(?:,(\d+))?\s+a\s+month/,
				MONTHLY_MIN: /From\s+₹(\d+)(?:,(\d+))?\s+a\s+month/,
				ANNUAL_RANGE: /₹(\d+)(?:,(\d+))?\s*-\s*₹(\d+)(?:,(\d+))?\s+a\s+year/,
				ANNUAL_MAX: /Up\s+to\s+₹(\d+)(?:,(\d+))?\s+a\s+year/,
			},
		},
		LOCATION: {
			PATTERN: /^(?:([^,]+),\s*)?([^,]+),\s*([^,]+)(?:,\s*(.*))?$/,
		},
	},
	JOB_NUMBER_START_FROM: 1,
	OPENAI: {
		MODELS: {
			EMBEDDING: 'text-embedding-ada-002',
			GPT_40_MINI: 'gpt-4o-mini',
			TEXT_DAVINCI: 'text-davinci-003',
		},
	},
	COORDINATES_TYPE: 'Point',
	AWS: {
		S3: {
			BUCKET_FOLDERS: {
				USER: 'user',
				RESUME: 'resume',
				PROFILE_IMAGE: 'profile-image',
				RESUME_BUILDER_THUMBNAIL: 'resume-builder-thumbnail',
				DELETED_USER: 'deleted-user',
				TEMP_USER: 'temp-user',
				DELETED_JOBS: 'deleted-jobs'
			},
		},
	},
}

export default constant
