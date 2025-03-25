import '@core/declarations'
import { CompanyPortals, I_Company } from '@models/company.model'
import Commitment from '@modules/cron/services/companies/collections/commitment.service'
import UpdateAmbitionboxCompany from '@modules/cron/services/companies/update-amibitionbox.service'

export default async function updateCompany() {
	try {
		const rawCompanies = await App.Models.RawCompany.find({
			isUpdated: true,
		}).limit(1000)
		if (rawCompanies.length) {
			Logger.info(`Found ${rawCompanies.length} companies for update.`)
			for (const rawCompany of rawCompanies) {
				const {portal, rawData} = rawCompany
				let companyObj: Partial<I_Company>
				if (portal == CompanyPortals.Glassdoor) {
					//
				} else if (portal == CompanyPortals.Crunchbase) {
					//
				} else if (portal == CompanyPortals.Ambitionbox) {
					const ambitionboxCompanyResp = await UpdateAmbitionboxCompany(rawData)
					if (ambitionboxCompanyResp.isSuccess) {
						// Check if commitment exist or not. If not exist then create
						const commitmentResp = await Commitment({
							nameArr: rawData.commitments,
						})
						companyObj = {
							portal,
							commitments: {
								_ids: commitmentResp && commitmentResp.length ? commitmentResp : [],
								names: rawData.commitments,
							},
							...ambitionboxCompanyResp.data,
						}
						await App.Models.Company.findOneAndUpdate(
							{id: rawData.id.toString()},
							companyObj, // Update object
							{
								new: true, // Return the updated document
								upsert: false, // Do not create a new document if none is found
							}
						)
                        rawCompany.isUpdated = false
						await rawCompany.save()
					}
				}
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
