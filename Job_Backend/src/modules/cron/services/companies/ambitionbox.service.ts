import { LogoHelperInstance } from '@helpers/logo.helper'
import { I_Company } from '@models/company.model'

export default async function AmbitionboxCompany(rawData: any) {
	try {
		if (rawData) {
			const offices: any = []
			if (rawData.location) {
				offices.push({
					location: rawData.location,
				})
			}
			const companyObj: Partial<I_Company> = {
				name: rawData.company_name || undefined,
				offices,
				industry: rawData.industry || undefined,
				description: rawData.description ? rawData.description.description : undefined,
				url: rawData.url || undefined,
				website: rawData.website || undefined,
				logo: rawData.logo || undefined,
				rating: rawData.rating || undefined,
				reviewsCount: rawData.reviewsCount || undefined,
				openings: rawData.openings || undefined,
				leadership:
					rawData.leadership && rawData.leadership.length ? rawData.leadership : [],
				companyInsight: rawData.companyInsight || undefined,
			}
			if (!companyObj.logo && companyObj.name) {
				companyObj.logo = await LogoHelperInstance.fetchLogo(companyObj.name)
			}
			return {
				isSuccess: true,
				data: companyObj,
			}
		}
	} catch (error) {
		Logger.error(error)
		return {
			isSuccess: false,
		}
	}
}
