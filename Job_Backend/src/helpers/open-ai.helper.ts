import OpenAI from 'openai'
import fs from 'fs'
import constant from '@core/constants'
import path from 'path'
import { S3Helper } from './aws-s3.helper'

class OpenAIHelper {
	private openai: any

	constructor() {
		// OpenAI configuration
		this.openai = new OpenAI({
			apiKey: App.Config.OPENAI.API_KEY,
		})
	}

	async getEmbedding(text: string): Promise<number[]> {
		try {
			const response = await this.openai.embeddings.create({
				model: constant.OPENAI.MODELS.EMBEDDING,
				input: text,
			})
			return response.data[0].embedding
		} catch (error) {
			Logger.error(error)
			throw new Error(error?.message ?? App.Messages.GeneralError.SomethingWentWrong())
		}
	}

	async getDesignationFromTitle(title: string): Promise<string> {
		try {
			const prompt = `
			Please Provide me with the valid designation mentioned in the following jobtitle.
			job title: ${title}
			Respond only exact designation. do not provide anything other than designation.
            `
			const response = await this.openai.chat.completions.create({
				model: constant.OPENAI.MODELS.GPT_40_MINI,
				messages: [{ role: 'user', content: prompt }],
			})

			if (response.choices && response.choices.length > 0) {
				return response.choices[0].message.content.trim()
			} else {
				throw new Error('No valid response from OpenAI.')
			}
		} catch (error) {
			Logger.error(error)
			throw new Error(error?.message ?? App.Messages.GeneralError.SomethingWentWrong())
		}
	}

	async retrieveBatch(batchId: string): Promise<any> {
		try {
			return await this.openai.batches.retrieve(batchId)
		} catch (error) {
			Logger.error(`Failed to retrieve batch status for batchId ${batchId}:`, error.message)
			throw new Error(error?.message ?? App.Messages.GeneralError.SomethingWentWrong())
		}
	}

	async retrieveFileContent(fileId: string): Promise<string> {
		try {
			return await this.openai.files.retrieveContent(fileId)
		} catch (error) {
			Logger.error(`Failed to retrieve file content for fileId ${fileId}:`, error.message)
			throw new Error(error?.message ?? App.Messages.GeneralError.SomethingWentWrong())
		}
	}

	async createBatch(tasks: Array<any>): Promise<any> {
		try {
			const data = tasks.map((task) => JSON.stringify(task)).join('\n')

			// const folderName = 'batches'
			const fileName = 'batch-input.jsonl'
			// const s3UploadResponse = await S3Helper.storeDataToS3({
			// 	folderName,
			// 	fileName,
			// 	data,
			// 	isPublic: false,
			// });

			// if (!s3UploadResponse.isSuccess) {
			// 	throw new Error('Failed to upload the batch file to S3.')
			// }

			const filePath = path.join(__dirname, fileName)
			fs.writeFileSync(filePath, data)

			const fileUploadResponse = await this.openai.files.create({
				file: fs.createReadStream(filePath),
				purpose: 'batch',
			})
			const fileId = fileUploadResponse.id
			const batchResponse = await this.openai.batches.create({
				input_file_id: fileId,
				endpoint: '/v1/chat/completions',
				completion_window: '24h',
			})
			const batchId = batchResponse.id

			return { fileId, batchId }
		} catch (error) {
			Logger.error(error)
			throw new Error(error?.message ?? App.Messages.GeneralError.SomethingWentWrong())
		}
	}
}

export const OpenaiHelper = new OpenAIHelper()
