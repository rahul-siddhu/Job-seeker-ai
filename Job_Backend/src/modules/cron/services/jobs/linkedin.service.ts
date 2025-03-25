export default async function LinkedinJob(rawData: any) {
	try {
		if (rawData) {
			return {
				isSuccess: true,
			}
		}
	} catch (error) {
		Logger.error(error)
		return {
			isSuccess: false,
		}
	}
}
