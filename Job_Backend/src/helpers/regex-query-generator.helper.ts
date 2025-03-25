import _ from 'lodash'

class RegexQueryGenerator {
	async Generate(inputs: { searchFields: any; excludeRegex?: any }) {
		const { searchFields, excludeRegex: exclude } = inputs

		/**
		 * ***************************************************
		 *        C R E A T E   F I L T E R   Q U E R Y
		 * ***************************************************
		 */
		const query: any = {}
		// Create regex filter query
		_.mapKeys(searchFields, (value, key) => {
			if (!_.isArray(query.$and)) {
				query.$and = []
			}
			const subQuery = {}
			// If the field is of type String, make it regex, else try to fetch it as it is.
			if (!exclude.includes(key) && typeof value === 'string') {
				subQuery[key] = { $regex: value, $options: 'i' }
			} else {
				subQuery[key] = value
			}
			query.$and.push(subQuery)
		})
		/**
		 * ***************************************************
		 *    E N D  C R E A T E   F I L T E R   Q U E R Y
		 * ***************************************************
		 */

		return query
	}
}

// All Done
export default new RegexQueryGenerator()
