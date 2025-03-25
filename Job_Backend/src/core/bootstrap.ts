import '@core/declarations'
import '@core/globals'
import { Application } from 'app'
import JWTHelper from '@helpers/jwt.helper'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default async (app: Application) => {
	// eslint-disable-line
	try {
		await Promise.all([
			JWTHelper.GenerateKeys(), // #2 Generate Public and Private Keys if don't exist
		])
	} catch (error) {
		Logger.error(error)
	}
}
