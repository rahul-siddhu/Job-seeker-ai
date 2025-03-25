import '@core/declarations'

class PaginationHelper {
	async Paginate(inputs: {
		q?: string
		model: string
		populate?: any
		startIndex?: number
		itemsPerPage?: number
		query?: any
		sort?: any
		projection?: any
	}) {
		try {
			const {
				q,
				model,
				populate = null,
				startIndex = 1,
				itemsPerPage = App.Config.ITEMS_PER_PAGE,
				query = {},
				sort = { _id: -1 },
				projection = {},
			} = inputs
			const Model: any = model

			const skipCount = Math.max(startIndex - 1, 0)
			const perPage = Math.max(itemsPerPage, App.Config.ITEMS_PER_PAGE)

			// Wild card search will be handled by fuzzy-search helper
			if (q) {
				query.$text = { $search: q }
				projection.confidence = { $meta: 'textScore' }
				sort.confidence = { $meta: 'textScore' }
			}

			const totalItems = await Model.countDocuments(query)

			let itemsQuery = Model.find(query, projection)
				.skip(skipCount)
				.limit(perPage)
				.sort(sort)
				.lean()

			if (populate) {
				itemsQuery = itemsQuery.populate(populate)
			}

			const items = await itemsQuery

			return {
				totalItems,
				startIndex: skipCount + 1,
				itemsPerPage: perPage,
				items,
			}
		} catch (error) {
			Logger.error(error)
			return null
		}
	}
}

// All Done
export default new PaginationHelper()
