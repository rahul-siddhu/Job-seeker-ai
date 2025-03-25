import { WorkModels } from '@models/job.model'

const tagRegex = (data: any) => {
	return new RegExp(`\\b(${data.join('|')})\\b`, 'gi')
}
export default function ExtractWorkModel(text: string) {
	let workModel = WorkModels.InOffice
	if (text && text != '') {
		const workFromHomeArr = ['remote', 'work from home', 'WFH']
		const hybridArr = ['hybrid']

		// WFH
		const workFromHomeReg = tagRegex(workFromHomeArr)
		if (workFromHomeReg.test(text)) workModel = WorkModels.FromHome

		// Hybrid
		const hybridReg = tagRegex(hybridArr)
		if (hybridReg.test(text)) workModel = WorkModels.Hybrid
	}
	return workModel
}
