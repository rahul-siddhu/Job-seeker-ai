declare namespace Express {
	export interface Response {
		[key: string]: any // eslint-disable-line
		success: CallableFunction
		created: CallableFunction
		forbidden: CallableFunction
		badRequest: CallableFunction
		notFound: CallableFunction
		internalServerError: CallableFunction
		unprocessableEntity: CallableFunction
		conflict: CallableFunction
		serviceUnavailable: CallableFunction
		tooManyRequests: CallableFunction
		unauthorized: CallableFunction
		invalidMongoId: CallableFunction
	}
	export interface Request {
		user: any // eslint-disable-line
		userSessionIdentifier: any // eslint-disable-line
		file: any // eslint-disable-line
		files: any // eslint-disable-line
		device: any // eslint-disable-line
		requestHash: string // eslint-disable-line
	}
}
