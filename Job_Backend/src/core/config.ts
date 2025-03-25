import '@core/declarations'
import { FileExistsSync } from './utils'

export interface ConfigInterface {
	HOST: string
	PORT: number
	ENVIRONMENT: string
	DB_CONNECTION_STRING: string
	DB_CONNECTION_OPTIONS: any

	AUTH_TOKEN: string
	OPENAI: {
		API_KEY: string
	}
	OLA_MAPS: {
		ENDPOINT: string
		API_KEY: string
	}

	ITEMS_PER_PAGE: number

	SALT_ROUNDS: number
	JWT_SECRET: string
	JWT_EXPIRY: string

	SUPPORT_EMAIL: string

	CRYPTO_SECRET_KEY: string
	AWS: {
		ACCESS_KEY: string
		SECRET_KEY: string
		REGION: string
		// SES_DEFAULT_FROM_EMAIL: string
		AWS_SES_SENDER_EMAIL: string
		BRAND_NAME: string
		S3_BUCKET_NAME: string
		SUPPORT_EMAIL: string
	}
	LOGO_DEV: {
		ENDPOINT: string
		API_KEY: string
	}
}

export default (): ConfigInterface => {
	const { NODE_ENV = 'development' } = process.env
	const environment = NODE_ENV?.toLowerCase()
	const environmentFileLocation = `${__dirname}/../environments`
	const environmentFilePath = `${environmentFileLocation}/${environment}`
	if (FileExistsSync(environmentFilePath)) {
		// eslint-disable-next-line
		const configuration: ConfigInterface = require(environmentFilePath).default()
		return configuration
	} else {
		Logger.error(`Missing environment file for NODE_ENV=${environment}.`)
		throw Error(`Missing environment file for NODE_ENV=${environment}.`)
	}
}
