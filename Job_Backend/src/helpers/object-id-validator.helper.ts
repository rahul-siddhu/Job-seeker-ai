import '@core/declarations'
import mongoose from 'mongoose'
const ObjectId = mongoose.Types.ObjectId

class ObjectIdValidationHelper {
	Validate(value: any, helpers: any) {
		if (!ObjectId.isValid(value)) {
			return helpers.message('"{{#value}}" is not a valid ObjectId')
		}
		return value
	}
}

// All Done
export default new ObjectIdValidationHelper()
