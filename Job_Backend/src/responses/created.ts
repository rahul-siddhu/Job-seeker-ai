import { Response } from 'express'

export default function (data = {}): Response {
	const statusCode = 201
	const {
		message = 'Created.',
		item = null,
		items = null,
	}: {
		message?: string
		referenceCode?: string
		isFirstLogin?: string
		token?: string
		item?: any
		items?: [any]
	} = data

	const resultant = {
		data: {
			message,
			statusCode,
			items: items ? items : item ? item : undefined,
		},
	}

	// All Done
	return this.status(statusCode).json(resultant)
}
