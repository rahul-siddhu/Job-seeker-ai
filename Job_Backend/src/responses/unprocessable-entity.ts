import { Response } from 'express'

export default function (data = {}): Response {
	const statusCode = 422
	const {
		message = 'Unprocessable Entity.',
		errors = null,
		item = null,
		items = null,
	}: {
		message?: string
		errors?: any
		item?: any
		items?: [any]
	} = data

	const extractedErrors = errors
		? errors.details.map((error: { message: string; context: { key: any } }) => ({
				message: error.message.replace(/"/g, ''),
				property: error.context.key,
		  }))
		: null
	const resultant = {
		error: {
			message: errors ? errors.details[0].message.replace(/"/g, '') + '.' : message,
			statusCode,
			errors: extractedErrors ? extractedErrors : undefined,
			items: items ? items : item ? [item] : undefined,
		},
	}

	// All Done
	return this.status(statusCode).json(resultant)
}
