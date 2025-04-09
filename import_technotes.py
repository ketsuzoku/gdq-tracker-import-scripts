import csv
import json
import urllib.parse
import urllib.request

csrf = b'<>' # Value of csrftoken=
cookie = b"csrftoken=<>; tracker_session=<>"
agent = b'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0' # Generic browser agent

technotes = []

# Replace filename with technote filename
with open('<filename>', 'r', encoding='utf-8') as f:
	r = csv.reader(f)
	for row in r:
		technotes.append(row)
	
# Our sheet has two header rows. If you have one header row, replace this with 'technotes = technotes[1:]'
technotes = technotes[2:]

# Note
# 0 - Game
# 1 - Run ID (unused)
# 2 - Release Year
# 3 - Layout
# 4 - Runner 1
# 5 - Runner 2
# 6 - Runner 3
# 7 - Runner 4
# 8 - Commentator 1
# 9 - Commentator 1 Pronouns
# 10 - Commentator 2
# 11 - Commentator 2 Pronouns
# 12 - Commentator 3
# 13 - Commentator 3 Pronouns
# 14 - NOTES: Camera (vtuber, pngtuber, keyboard camera etc. leave blank if webcam is used)
# 15 - NOTES: Start
# 16 - NOTES: End
# 17 - NOTES: Content
# 18 - NOTES: Tech
# 19 - NOTES: Incentives

for note in technotes:

	if note[0].rstrip() == '':
		continue

	commentators = []
	headsets = []

	if note[8].strip() != '':
		commentators.append({'name': note[8].strip(), 'pronouns': note[9].strip() or ""})
		headsets.append(note[8].strip())
	if note[10].strip() != '':
		commentators.append({'name': note[10].strip(), 'pronouns': note[11].strip() or ""})
		headsets.append(note[10].strip())
	if note[12].strip() != '':
		commentators.append({'name': note[12].strip(), 'pronouns': note[13].strip() or ""})
		headsets.append(note[12].strip())		

	# Similarly to how runner import works, case sensitivity is a thing so we need to compare to the correct case
	for commentator in commentators:

		headsetrequest = urllib.request.Request(url=f'<url to talent endpoint>?name={urllib.parse.quote(commentator["name"])}')
		headsetrequest.add_header('Cookie', cookie)
		headsetrequest.add_header('User-Agent', agent)
		headsetrequest.add_header('X-CSRFToken', csrf)
		headsetrequest.add_header('Referer', '<url to admin site>')

		try: 
			with urllib.request.urlopen(headsetrequest) as url:
				headsetinfo = json.loads(url.read())
				print(f"Status code: {url.code}")
				print(f"Result: {url.read()}\n")
		except urllib.request.HTTPError as e:
			print(f"Status code: {e.code}")
			print(f"URL: {e.url}")
			print(f"Error {e.file.read()}\nInput: {data}\n")

		if headsetinfo['count'] > 0 and any(commentator['name'].lower() == headsetinfo['results'][i]['name'].lower() for i in range(0,headsetinfo['count'])):

			print('Headset info for ' + commentator['name'] + ' exists, updating.')

			id = ""
			for entry in headsetinfo['results']:
				if entry['name'].lower() == commentator['name'].lower():
					id = entry['id']


			print('ID: ' + str(id))
			query = {
				'name': commentator['name'],
				'pronouns': commentator['pronouns']
			}
			
			data = json.dumps(query).encode('utf-8')
	
			req = urllib.request.Request(url=f'<url to talent endpoint>/{id}/', data=data, method='PATCH')
			req.add_header('Cookie', cookie)
			req.add_header('User-Agent', agent)
			req.add_header('Content-Type','application/json')
			req.add_header('X-CSRFToken', csrf)
			req.add_header('Referer','<url to admin site>')
	
			try:
				with urllib.request.urlopen(req) as f:
					print(f"Status code: {f.code}")
					print(f"Result: {f.read()}\n")		
			except urllib.request.HTTPError as e:
				print(f"Status code: {e.code}")
				print(f"URL: {e.url}")
				print(f"Error: {e.file.read()}\nInput: {data}\n")
			
			
	
		else:
			
			print('Headset info for ' + commentator['name'] + ' does not exist, creating new entry.')
			
			query = {
				'name': commentator['name'],
				'pronouns': commentator['pronouns']
			}

			data = json.dumps(query).encode('utf-8')
	
			req = urllib.request.Request(url='<url to talent endpoint>', data=data, method='POST')
			req.add_header('Cookie', cookie)
			req.add_header('User-Agent', agent)
			req.add_header('Content-Type', 'application/json')
			req.add_header('X-CSRFToken',csrf)
			req.add_header('Referer','<url to admin site>')
	
			try:
				with urllib.request.urlopen(req) as f:
					print(f"Status code: {f.code}")
					print(f"Result: {f.read()}\n")		
			except urllib.request.HTTPError as e:
				print(f"Status code: {e.code}")
				print(f"URL: {e.url}")
				print(f"Error: {e.file.read()}\nInput: {data}\n")
	
	#note order:
	# Camera - 14
	# Content - 17
	# Tech - 18
	# Incentives - 19
	# Start - 15
	# End - 16
	noteorder = [14, 17, 18, 19, 15, 16]

	notes = ""

	for i in noteorder:
		if note[i].strip() != "":
			notes+=note[i].strip()+'\n\n'

	fin = notes.strip()
	
	query = {
		'tech_notes': fin
	}

	if note[3].strip() != "":
		query.update({'layout': note[3].strip()})
	
	if note[2].strip() != "":
		query['release_year'] = note[2].strip()

	if commentators:
		query['commentators'] = headsets
	

	data = json.dumps(query).encode('utf-8')
	
	req = urllib.request.Request(url=f'<url to runs endpoint>/{note[2].strip()}/', data=data, method='PATCH')
	req.add_header('Content-Type', 'application/json')
	req.add_header('Cookie', cookie)
	req.add_header('User-Agent', agent)
	req.add_header('X-CSRFToken', csrf)
	req.add_header('Referer', '<url to admin site>')


	try:
		with urllib.request.urlopen(req) as f:
			print(f"Status code: {f.code}")
			print(f"Result: {f.read()}\n")		
	except urllib.request.HTTPError as e:
		print(f"Status code: {e.code}")
		print(f"URL: {e.url}")
		print(f"Error: {e.file.read()}\nInput: {data}\n")
	