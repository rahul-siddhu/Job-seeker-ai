import * as CryptoJS from 'crypto-js'

const key = App.Config.CRYPTO_SECRET_KEY
const keyutf = CryptoJS.enc.Utf8.parse(key)
const iv = CryptoJS.enc.Base64.parse(key)

const encrypt = (plaintext: string) => {
	const ciphertext = CryptoJS.AES.encrypt(plaintext, keyutf, { iv: iv }).toString()
	const encoded = CryptoJS.enc.Base64.parse(ciphertext).toString(CryptoJS.enc.Hex)
	return encoded
}

const decrypt = (encodedText: string) => {
	const decoded = CryptoJS.enc.Hex.parse(encodedText).toString(CryptoJS.enc.Base64)
	const plaintext = CryptoJS.AES.decrypt(
		{ ciphertext: CryptoJS.enc.Base64.parse(decoded) },
		keyutf,
		{ iv: iv }
	).toString(CryptoJS.enc.Utf8)
	return plaintext
}

export { encrypt, decrypt }
