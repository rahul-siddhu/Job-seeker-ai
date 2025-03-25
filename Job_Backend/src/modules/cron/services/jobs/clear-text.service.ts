import natural from 'natural'

const removeStopWords = (text: string) => {
	const stopwords = natural.stopwords

	const tokenizer = new natural.WordTokenizer() // Tokenizer to split words
	const words = tokenizer.tokenize(text.toLowerCase()) // Tokenize and lowercase
	return words.filter((word) => !stopwords.includes(word)).join(' ') // Filter stop words and rejoin
}

export async function ClearText(text: string) {
	// let vectorArr = []
	const cleanText = removeStopWords(text)
		.toLowerCase() // Convert to lowercase
		.split(/\s+/) // Split text into words
		.filter((value, index, self) => self.indexOf(value) === index) // Remove duplicates
		.join(' ')
	return cleanText
}
