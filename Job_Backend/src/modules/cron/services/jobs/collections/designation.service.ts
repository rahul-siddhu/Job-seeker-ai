// import { OpenaiHelper } from '@helpers/open-ai.helper'

export default async function Designation(data: any) {
	try {
		const { name } = data
		const designation = await App.Models.Designation.findOne({
			name: { $regex: name.toString(), $options: 'i' },
		})
		if (!designation) {
			// Extract the designation from job title: chatgpt
			// name = await OpenaiHelper.getDesignationFromTitle(name)
			// designation = await App.Models.Designation.findOne({
			// 	name: { $regex: name.toString(), $options: 'i' },
			// })
			// if (!designation) {
			// 	designation = new App.Models.Designation({
			// 		name,
			// 	})
			// 	await designation.save()
			// }
		}

		return designation
	} catch (error) {
		Logger.error(error)
		return error
	}
}
