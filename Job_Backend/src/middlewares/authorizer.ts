import '@core/declarations'
import { Request, Response, NextFunction } from 'express'

export const authorize = async (req: Request, res: Response, next: NextFunction) => {
	try {
		if (!req.headers.authorization) {
			return res.unauthorized()
		}
		const token = req.headers.authorization.split(' ')[1]

		const authToken = App.Config.AUTH_TOKEN

		if (token.toString() != authToken.toString()) {
			return res.unauthorized()
		}

		return next()
	} catch (error) {
		Logger.error(error)
		return res.internalServerError({ error })
	}
}
