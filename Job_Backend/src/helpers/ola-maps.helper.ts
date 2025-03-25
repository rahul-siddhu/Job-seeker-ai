import axios from 'axios'

class OlaMaps {
	private apiKey: string

	constructor() {
		this.apiKey = App.Config.OLA_MAPS.API_KEY
	}

	async getLatLong(address: string): Promise<any> {
		try {
			const params = {
				address,
				language: 'English',
				api_key: this.apiKey,
			}
			const config = {
				url: `${App.Config.OLA_MAPS.ENDPOINT}/places/v1/geocode`,
				method: 'GET',
				params,
				headers: {
					'Content-Type': 'application/json',
				},
			}
			const response = await axios(config)
			if (response.data.geocodingResults && response.data.geocodingResults.length) {
				const location = response.data.geocodingResults[0].geometry.location
				return {
					lat: location.lat,
					long: location.lng,
				}
			}
			return null
		} catch (error) {
			Logger.error(error)
			return null
		}
	}
}

export const OlaMapsHelper = new OlaMaps()
