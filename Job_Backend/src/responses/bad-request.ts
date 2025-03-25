import { Response } from 'express'

export default function (data = {}): Response {
	const statusCode = 400
	const {
		message = 'Bad Request.',
		error = null,
		errors = null,
		item = null,
		items = null,
	}: {
		message?: string
		error?: any
		errors?: any[]
		item?: any
		items?: any[]
	} = data

	const resultant = {
		error: {
			message,
			statusCode,
			errors: errors ? errors : error ? [error] : undefined,
			items: items ? items : item ? item : undefined,
		},
	}

	// All Done
	return this.status(statusCode).json(resultant)
}
