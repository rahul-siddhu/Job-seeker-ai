import { ConfigInterface } from '@config'

const APP_PORT: number = parseInt(process.env.DEV_PORT)
const DOMAIN_NAME: string = process.env.DOMAIN_NAME ?? 'localhost'
const HTTP_PROTOCOL: string = process.env.HTTP_PROTOCOL ?? 'http'

export default (): ConfigInterface => {
	process.env['NODE_ENV'] = 'development'

	return {
		HOST:
			process.env.HOST ??
			`${HTTP_PROTOCOL}://${DOMAIN_NAME}${APP_PORT == 80 ? '' : `:${APP_PORT}`}`,
		PORT: APP_PORT,
		ENVIRONMENT: process.env['NODE_ENV'],
		DB_CONNECTION_STRING: process.env.DEV_DB_CONNECTION_STRING,
		DB_CONNECTION_OPTIONS: {
			useNewUrlParser: true,
			useUnifiedTopology: true,
		},
		AUTH_TOKEN: process.env.AUTH_TOKEN,
		OPENAI: {
			API_KEY: process.env.OPENAI_API_KEY,
		},
		OLA_MAPS: {
			ENDPOINT: process.env.API_ENDPOINT,
			API_KEY: process.env.API_KEY,
		},

		ITEMS_PER_PAGE: parseInt(process.env.ITEMS_PER_PAGE) || 10,
		SALT_ROUNDS: parseInt(process.env.SALT_ROUNDS),
		JWT_SECRET: process.env.JWT_SECRET,
		JWT_EXPIRY: process.env.JWT_EXPIRY,

		SUPPORT_EMAIL: process.env.SUPPORT_EMAIL,

		CRYPTO_SECRET_KEY: process.env.CRYPTO_SECRET_KEY,
		AWS: {
			ACCESS_KEY: process.env.AWS_ACCESS_KEY,
			SECRET_KEY: process.env.AWS_SECRET_KEY,
			REGION: process.env.AWS_REGION,
			// SES_DEFAULT_FROM_EMAIL: process.env.AWS_SES_DEFAULT_FROM_EMAIL,
			AWS_SES_SENDER_EMAIL: process.env.AWS_SES_SENDER_EMAIL,
			BRAND_NAME: process.env.AWS_BRAND_NAME || 'Joblo AI',
			S3_BUCKET_NAME: process.env.AWS_S3_BUCKET,
			SUPPORT_EMAIL: process.env.AWS_SES_SUPPORT_EMAIL,
		},
		LOGO_DEV: {
			ENDPOINT: process.env.LOGO_API_URL,
			API_KEY: process.env.LOGO_API_KEY,
		},
	}
}
