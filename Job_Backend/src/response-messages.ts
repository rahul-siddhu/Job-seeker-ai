import Config, { ConfigInterface } from '@config'
const config: ConfigInterface = Config()

export const Messages = {
	GeneralError: {
		Unauthorized: 'Unauthorized',
		SomethingWentWrong: 'Something went wrong.',
		BadRequest: 'Bad Request',
		AccountBlockedByAdmin: `Your account has been deactivated by the administrator, for more updates kindly contact ${config.SUPPORT_EMAIL}.`,
		SessionExpired: 'This session has expired!',
	},
}
