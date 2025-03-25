export default async function Skill(data: any) {
	try {
		const { names } = data
		const skillsArr = []

		if (names && names.length) {
			for (let i = 0; i < names.length; i++) {
				const name = names[i]

				let skill = await App.Models.Skill.findOne({
					name: { $regex: name.toString(), $options: 'i' },
				})
				if (!skill) {
					skill = new App.Models.Skill({
						name,
					})
					await skill.save()
				}
				skillsArr.push(skill._id)
			}
		}

		return skillsArr
	} catch (error) {
		Logger.error(error)
		return error
	}
}
