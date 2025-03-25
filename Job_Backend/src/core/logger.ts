import '@core/declarations'
import winston from 'winston'
import Config, { ConfigInterface } from '@core/config'
const config: ConfigInterface = Config()

import Dayjs from 'dayjs'
import DayjsUtcPlugin from 'dayjs/plugin/utc'
import DayjsTimezonePlugin from 'dayjs/plugin/timezone'

Dayjs.extend(DayjsUtcPlugin)
Dayjs.extend(DayjsTimezonePlugin)

const NODE_ENV = config.ENVIRONMENT
const LOG_TIMEZONE = process.env['LOG_TIMEZONE'] || 'Asia/Kolkata'

const WINSTON_TIMEZONE = () => {
	return Dayjs().tz(LOG_TIMEZONE).format('YY-MM-DD hh:mm:ss A')
}

const WINSTON_FORMAT = winston.format.combine(
	winston.format.errors({ stack: true }),
	winston.format.label({ label: '' }),
	winston.format.timestamp({ format: WINSTON_TIMEZONE }),
	winston.format.printf(
		(log) =>
			` [IST ${log.timestamp}][${NODE_ENV[0]?.toUpperCase()}] ${log.message} ${
				log.stack ?? ''
			}`
	)
)

export const Logger = winston.createLogger({
	exitOnError: false,
	format: WINSTON_FORMAT,
	transports: [
		new winston.transports.Console({
			format: winston.format.combine(winston.format.colorize({ all: true })),
			level: 'info',
		}),
	].filter((e) => e != undefined),
})
