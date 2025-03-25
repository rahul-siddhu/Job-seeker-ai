import databaseService from '@helpers/database-factory.helper'
import { LogoHelperInstance } from '@helpers/logo.helper'

export default async function Company(data: any) {
	try {
		const { name, location } = data
		if (name && name != '') {
			let company = await App.Models.Company.findOne({
				name: databaseService.exactCaseInsensitiveSearchObj(name),
			})
			if (!company) {
				const offices = [
					{
						location,
					},
				]
				const logo = await LogoHelperInstance.fetchLogo(name)

				company = new App.Models.Company({
					name,
					offices,
					logo,
				})
				company = await company.save()
			}

			return company
		}
		return null
	} catch (error) {
		Logger.error(error)
		return error
	}
}
