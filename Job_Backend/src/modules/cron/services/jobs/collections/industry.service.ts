export default async function Industry(data: any) {
	try {
		const { name } = data
		const industry = await App.Models.Industry.findOne({
			name: { $regex: name.toString(), $options: 'i' },
		})
		if (!industry) {
			return null
		}

		return industry
	} catch (error) {
		Logger.error(error)
		return error
	}
}
