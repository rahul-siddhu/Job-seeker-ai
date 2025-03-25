import '@core/declarations'
import { CompanyPortals, I_Company } from '@models/company.model'
import AmbitionboxCompany from '../../services/companies/ambitionbox.service'
import Commitment from '../../services/companies/collections/commitment.service'

export default async function Companies() {
	try {
		const rawCompanies = await App.Models.RawCompany.find({
			isDumped: false,
		}).limit(10)
		if (rawCompanies.length) {
			Logger.info('Cron: Raw data found for company')
			for (const rawCompany of rawCompanies) {
				const portal = rawCompany.portal
				const rawData = rawCompany.rawData

				let companyObj: Partial<I_Company>
				if (portal == CompanyPortals.Glassdoor) {
					//
				} else if (portal == CompanyPortals.Crunchbase) {
					//
				} else if (portal == CompanyPortals.Ambitionbox) {
					const ambitionboxCompanyResp = await AmbitionboxCompany(rawData)
					if (ambitionboxCompanyResp.isSuccess) {
						// Check if job function exist or not. If not exist then create
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

						// Check if company is already exist
						const oldCompany = await App.Models.Company.findOne({
							name: {$regex: companyObj.name.toString(), $options: 'i'},
						})
						if (oldCompany) {
							// Update the company with new data
							await App.Models.Company.findByIdAndUpdate(oldCompany._id, companyObj, {
								new: true,
							})
						} else {
							// Create a new company
							await App.Models.Company.create(companyObj)
						}
						rawCompany.isDumped = true
						await rawCompany.save()
					}
				}
			}
		}
	} catch (error) {
		Logger.error(error?.message)
	}
}
