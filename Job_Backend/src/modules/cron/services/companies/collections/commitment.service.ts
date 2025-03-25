export default async function Commitment(data: any) {
	try {
		const { nameArr } = data
		const commitmentIdArr = []
		if (nameArr && nameArr.length) {
			for (let i = 0; i < nameArr.length; i++) {
				const name = nameArr[i]
				let commitment = await App.Models.Commitment.findOne({
					name: { $regex: name.toString(), $options: 'i' },
				})
				if (!commitment) {
					commitment = new App.Models.Commitment({
						name,
					})
					await commitment.save()
				}
				commitmentIdArr.push(commitment._id.toString())
			}
		}

		return commitmentIdArr
	} catch (error) {
		Logger.error(error)
		return error
	}
}
