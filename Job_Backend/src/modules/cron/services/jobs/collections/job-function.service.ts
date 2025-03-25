export default async function JobFunction(data: any) {
	try {
		const { name } = data
		const jobFunction = await App.Models.JobFunction.findOne({
			name: { $regex: name.toString(), $options: 'i' },
		})
		if (!jobFunction) {
			return null
		}

		return jobFunction
	} catch (error) {
		Logger.error(error)
		return error
	}
}
