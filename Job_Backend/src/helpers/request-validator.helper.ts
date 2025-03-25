import Joi from 'joi'

const requestValidator = async (schema: Joi.ObjectSchema, data = {}) => {
	try {
		await schema.validateAsync(data, { abortEarly: false })
		return null
	} catch (error) {
		Logger.error(error)
		return error
	}
}

export default requestValidator
