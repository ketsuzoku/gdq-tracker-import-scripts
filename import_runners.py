import csv
import json
import urllib.request

cookie = b'tracker_session=<>; csrftoken=<>'
csrftoken = '<>' # Value of csrftoken=
agent = b'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0' # Generic browser agent

data = []
runners = {}

# Replace filename with runner info sheet name
with open('<filename>', 'r', encoding='utf-8') as f:
	r = csv.reader(f)
	for row in r:
		data.append(row)

data = data[1:]

# Runner Information Sheet Format
# Runner Name - Case Sensitive
# Runner Pronouns
# Stream Link
# Twitter Name

for runner in data:

	name = runner[0].strip()
	pronouns = runner[1].strip() or ""
	stream = f"https://twitch.tv/{runner[2].strip().lower()}" or ""
	twitter = runner[3].strip() or ""

	runners[name] = { 'stream': stream, 'twitter': twitter, 'pronouns': pronouns }
	
	
for runner, info in runners.items():

	runnerid = ""

	# Search the runner list for existing entries; 
	runnerrequest = urllib.request.Request(url='<url to talent endpoint>'.format(urllib.parse.quote(runner)))
	runnerrequest.add_header('Cookie', cookie)
	runnerrequest.add_header('User-Agent', agent)
	runnerrequest.add_header('X-CSRFToken', csrftoken)
	runnerrequest.add_header('Referer', '<url to site>')

	try: 
		with urllib.request.urlopen(runnerrequest) as url:
			runnerinfo = json.loads(url.read())
			statuscode = url.code
	except urllib.request.HTTPError as e:
		print(f"Status code: {e.code}")
		print(f"Error: {e.file.read()}")

	#print(runnerinfo)

	# Case sensitivity is awkward. This grabs the appropriate name if the case is different to what is included on the sheet.
	if runnerinfo['count'] > 0 and any(runner in runnerinfo['results'][i]['name'] for i in range(0,runnerinfo['count'])):

		for entry in runnerinfo['results']:
			if entry['name'] == runner:
				runnerid = entry['id']

		query = {
			'name': runner,
			'stream': info['stream'],
			'twitter': info['twitter'],
			'pronouns': info['pronouns']
		}
		
		data = json.dumps(query).encode('utf-8')
		
		req = urllib.request.Request(url=f'<url to talent endpoint>/{str(runnerid)}/', data=data, method='PATCH')
		req.add_header('Cookie', cookie)
		req.add_header('User-Agent', agent)
		req.add_header('Content-Type','application/json')
		req.add_header('X-CSRFToken', csrftoken)
		req.add_header('Referer', '<url to admin website>')

		try:
			with urllib.request.urlopen(req) as f:
				print(f"Status code: {f.code}")
				print(f"Result: {f.read()}")
		except urllib.request.HTTPError as e:
			print(f"Status code: {e.code}")
			print(f"URL: {e.url}")
			print(f"Error: {e.file.read()}\nInput: {data}")
	
	# New runner entry
	else:
		
		query = {
			'name': runner,
			'stream': info['stream'],
			'twitter': info['twitter'],
			'pronouns': info['pronouns']
		}
		
		data = json.dumps(query).encode('utf-8')
	
		req = urllib.request.Request(url='<url to talent endpoint>', data=data, method='POST')
		req.add_header('Cookie', cookie)
		req.add_header('User-Agent', agent)
		req.add_header('Content-Type','application/json')
		req.add_header('X-CSRFToken', csrftoken)
		req.add_header('Referer', '<url to admin website>')
		
		try:
			with urllib.request.urlopen(req) as f:
				print(f"Status code: {f.code}")
				print(f"Result: {f.read()}")		
		except urllib.request.HTTPError as e:
			print(f"Status code: {e.code}")
			print(f"URL: {e.url}")
			print(f"Error: {e.file.read()}\nInput: {data}")