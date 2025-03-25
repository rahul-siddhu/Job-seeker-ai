import { Model } from 'mongoose'

interface aggregationFilter {
	startDate: string
	endDate: string
}

export type AggregationPagination = {
	_startIndex: number
	_itemsPerPage: number
	query: Array<any>
	sortObj?: object
	projection?: object
}
const databaseService = {
	exactCaseInsensitiveSearchObj: (searchValue: string) => {
		const query = { $regex: `^${searchValue.trim()}$`, $options: 'i' }
		return query
	},
	aggregationQuery: async (model: Model<any>, query: Array<any>) => {
		const data = await model.aggregate(query)
		return data
	},
	aggregationSearch: (fieldArray: Array<any>, searchValue: string) => {
		const query = {
			$match: {
				$or: [
					...fieldArray.map((field) => ({
						[field]: { $regex: searchValue, $options: 'i' },
					})),
				],
			},
		}
		return query
	},
	aggregationFilterDate: (queries: aggregationFilter, fieldName: string) => {
		const query = {
			$match: {
				[fieldName]: {
					$gte: new Date(queries.startDate),
					$lte: new Date(queries.endDate),
				},
			},
		}
		return query
	},
	aggregationSkipLimit: (query: any) => {
		const facetObject = {
			$facet: {
				list: [
					{ $skip: (Number(query.startIndex) - 1) * Number(query.itemsPerPage) || 0 },
					{ $limit: Number(query.itemsPerPage) || Number(App.Config.ITEMS_PER_PAGE) },
					{ $sort: { _id: -1 } },
				],

				totalItem: [{ $count: 'count' }],
			},
		}
		return facetObject
	},
	aggregationLimit: (limit: any) => {
		const query = {
			$limit: limit,
		}
		return query
	},
	aggregationLookup: (
		from: string,
		localField: string,
		foreignField: string,
		asString: string,
		pipeline: any = [],
		preserveNullAndEmptyArrays = true
	) => {
		const obj = [
			{
				$lookup: {
					from,
					localField,
					foreignField,
					pipeline,
					as: asString,
				},
			},
			{
				$unwind: {
					path: `$${asString}`,
					preserveNullAndEmptyArrays,
				},
			},
		]
		return obj
	},
	aggregationMatch: (matchCondition: object) => {
		const matchObj = {
			$match: matchCondition,
		}
		return matchObj
	},
	aggregationGroup: (dataObj: any) => {
		const query = {
			$group: dataObj,
		}
		return query
	},
	aggregationProject: (dataObj: any) => {
		const query = {
			$project: dataObj,
		}
		return query
	},
	aggregationSort: (dataObj: any) => {
		const query = {
			$sort: dataObj,
		}
		return query
	},
	aggregationPagination: async (inputs: AggregationPagination, model: Model<any>) => {
		const perPage = inputs._itemsPerPage > 0 ? inputs._itemsPerPage : App.Config.ITEMS_PER_PAGE
		const skipCount: number = inputs._startIndex > 0 ? (inputs._startIndex - 1) * perPage : 0
		const facetObj = {
			$facet: {
				list: [
					{
						$project: inputs.projection,
					},
					{
						$sort: inputs.sortObj || { _id: -1 },
					},
					{
						$skip: skipCount,
					},
					{
						$limit: perPage,
					},
				],
				totalItems: [
					{
						$count: 'count',
					},
				],
			},
		}
		const query = inputs.query
		query.push(facetObj)
		const data = await model.aggregate(inputs.query)
		return {
			totalItems: data[0]?.totalItems[0]?.count,
			startIndex: inputs._startIndex || 1,
			itemsPerPage: perPage,
			totalPage: Math.ceil(data[0]?.totalItems[0]?.count / inputs._itemsPerPage),
			data: data[0]?.list,
		}
	},
	aggregationAddFields: (inputs: any) => {
		const query = {
			$addFields: inputs,
		}
		return query
	},
	generateSearchQuery: (query: string, index: string, path: string = '*') => {
		const _query = {
			$search: {
				index,
				text: {
					query,
					path: {
						wildcard: path,
					},
				},
			},
		}

		return _query
	},
}
export default databaseService
