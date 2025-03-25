import { Response } from 'express'

export default function (data = {}): Response {
	const statusCode = 503
	const {
		message = 'Server is in maintenance mode.',
		error = null,
		errors = null,
		item = null,
		items = null,
	}: {
		message?: string
		error?: any
		errors?: any[]
		item?: any
		items?: [any]
	} = data

	const resultant = {
		error: {
			message,
			statusCode,
			errors: errors ? errors : error ? [error.toString()] : undefined,
			items: items ? items : item ? [item] : undefined,
		},
	}

	// All Done
	return this.status(statusCode).json(resultant)
}
