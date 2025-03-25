import axios from 'axios'

class LogoHelper {
	private apiKey: string
	private apiUrl: string

	constructor() {
		this.apiKey = App.Config.LOGO_DEV.API_KEY
		this.apiUrl = App.Config.LOGO_DEV.ENDPOINT
	}

	async fetchLogo(companyName: string): Promise<string | null> {
		try {
			const params = { q: companyName }
			const config = {
				url: this.apiUrl,
				method: 'GET',
				params,
				headers: {
					Authorization: `Bearer ${this.apiKey}`,
					'Content-Type': 'application/json',
				},
			}
			const response = await axios(config)

			if (response?.data?.length) {
				return response.data[0]?.logo_url || null
			}

			return null
		} catch (error) {
			Logger.error(`Error fetching logo for company "${companyName}":`, error)
			return null
		}
	}
}

export const LogoHelperInstance = new LogoHelper()
