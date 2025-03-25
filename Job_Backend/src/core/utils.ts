import '@core/declarations'
import { Request, Response, NextFunction } from 'express'
import fs from 'node:fs'
import Mustache from 'mustache'
import axios from 'axios'
import Crypto from 'node:crypto'
import constant from './constants'

export const FileExistsSync = (FilePath) => {
	return fs.existsSync(`${FilePath}.js`) || fs.existsSync(`${FilePath}.ts`)
}

export function GenerateRandomStringOfLength(length) {
	let result = ''
	const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	const charactersLength = characters.length
	for (let i = 0; i < length; i++) {
		result += characters.charAt(Math.floor(Math.random() * charactersLength))
	}
	return result
}

export function GenerateRandomNumberOfLength(length) {
	let result = ''
	const characters = '0123456789'
	const charactersLength = characters.length
	for (let i = 0; i < length; i++) {
		result += characters.charAt(Math.floor(Math.random() * charactersLength))
	}
	return result
}

export function Wrap(controller: CallableFunction) {
	return async (req: Request, res: Response, next: NextFunction) => {
		try {
			await controller(req, res, next)
		} catch (error) {
			Logger.error(error)
			return res.internalServerError({ error })
		}
	}
}

export function GenerateCallableMessages(_Messages: any) {
	const Messages: { [key: string]: any } = {}

	function _GenerateCallableMessages(target: any, values: { [key: string]: any }) {
		try {
			for (const key in values) {
				if (typeof values[key] == 'string') {
					target[key] = (params: { [key: string]: string }) => {
						return Mustache.render(values[key], params)
					}
				} else {
					target[key] = {}
					_GenerateCallableMessages(target[key], values[key])
				}
			}
		} catch (error) {
			Logger.error(error)
		}
	}

	_GenerateCallableMessages(Messages, _Messages)
	return Messages
}

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

export function GetKeyByValue(o: any, v: any) {
	return Object.keys(o).find((key) => o[key] === v)
}

export async function GeolocationByIp(ip: string): Promise<{ [key: string]: string } | undefined> {
	const { data: geolocationResponse } = await axios.get(`http://ip-api.com/json/${ip}`)
	if (geolocationResponse.status == 'success') {
		geolocationResponse.address = [
			geolocationResponse?.regionName,
			geolocationResponse?.city,
			geolocationResponse?.country,
			geolocationResponse?.zip,
		]
			.filter((e) => e != undefined)
			.join(', ')
		return geolocationResponse
	} else {
		return undefined
	}
}

export function GenerateHashFrom(params: any) {
	if (!Array.isArray(params)) {
		params = [params]
	}

	params = params
		.filter((e: any) => e != undefined || e != null)
		.sort()
		.map((e: any) => e.toString())
		.join('-')
	return Crypto.createHash('sha256').update(params.toString()).digest('hex')
}

export async function jobNumberIncrementer() {
	const job = await App.Models.Job.findOne().sort({ number: -1 }).select('number').lean()
	let incrementedNumber = constant.JOB_NUMBER_START_FROM
	if (job) {
		incrementedNumber = job.number + 1
	}
	return Number(incrementedNumber)
}

export function getFirstWords(input: string, length: number) {
	const words = input.split(/\s+/)
	const extractedWords = words.slice(0, length).join(' ')
	return extractedWords
}
