import csv
import json
import urllib.parse
import urllib.request

cookie = b'' # tracker_session=x; csrftoken=x
csrftoken = b'' # value of csrftoken
agent = b'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0' # generic browser agent
cid = '' # twitch client id from developer app 
csec = '' # twitch client secret from developer app
oauth = ''
responselist = []
event = 0 # Replace with numeric id of event
runs = []
data = {}

# This section grabs a twitch oauth key. If you don't want to check your run list against twitch's database, you can skip this step.
twquery = {
	'client_id': cid,
	'client_secret': csec,
	'grant_type': 'client_credentials'
}

twqstr = urllib.parse.urlencode(twquery)
twq = bytearray(twqstr, 'utf-8')

twreq = urllib.request.Request(url='https://id.twitch.tv/oauth2/token', data=twq, method='POST')
try:
	with urllib.request.urlopen(twreq) as f:
		res = json.loads(f.read())
		oauth = res['access_token']
except urllib.request.HTTPError as e:
	print(e.file.read(), twq)
		


# Put the filename of your schedule sheet here.
with open('<filename>', 'r', encoding='utf-8') as f:
	r = csv.reader(f)
	for row in r:
		runs.append(row)

# Spreadsheet Column Format, You can use your own but make sure the you adjust list indices appropriately in code.
# 0 - Run Timestamp (unused in code as tracker makes those calculations automatically)
# 1 - Platform (console that run will be performed on)
# 2 - Online (is run online or in person?)
# 3 - Block Label (unused in code)
# 4 - Game Name
# 5 - Run Category
# 6 - Runners (needs to be a comma separated list of runners)
# 7 - Run Estimate (format hH:MM:SS)
# 8 - Post-Game Setup (Unused in code, used on the sheet alongside incentive time to calculate total setup time)
# 9 - Tags (used to describe the run, I believe tags need to be created before import)
# 10 - Setup to Import (combines the values from Post-Game Setup and Incentive Time)
# 11 - Full Stage? (unused in code)
# 12 - Additional Tech Setup (unused)
# 13 - Incentive Time (part of total setup time, unused in code)
# 14 - Interstitial After Game (not used in code)
# 15 - Co-op Run (if the run features multiple runners playing collaboratively instead of it being a race)


order = "last" # This automatically appends new runs to the end of the schedule. You can replace this with a specific number to insert a run inside... I think that works? Better to use the schedule editor though.
runs = runs[1:]

for run in runs:

	# Tags
	tags = []
	if run[9].strip():
		tags.extend(run[9].lower().replace('"',"").replace(", ",",").rstrip().split(','))
	
	# Game Name
	name = run[4].strip()

	# Online Status
	if run[2].strip() == "Yes":
		online = 'ONLINE'
	elif run[2].strip() == "No":
		online = 'ONSITE'
	else:
		online = 'HYBRID'

	# Co-op Status
	coop = run[15] if run[15] == "Yes" else None

	# Runner List
	runners = run[9].replace('"',"").replace(", ",",").rstrip().split(",")

	# Query Format - You can find the list of fields in https://github.com/GamesDoneQuick/donation-tracker/blob/master/tracker/models/event.py, in the class Speedrun() section.
	query = {
		'name': name,
		'onsite': online,
		'category': run[5].rstrip(),
		'run_time': run[7],
		'setup_time': run[10] or '00:00:00',
		'console': run[1].rstrip(),
		'order': order,
		'runners': runners,
		'event': event
	}

	# If coop, add to the query
	if coop:
		query.update({'coop': 'True'})

	# If the run has tags, add to the query
	if tags:
		query.update({ 'tags': tags })

	
	data = json.dumps(query).encode('utf-8')

	# Make sure you replace the url and Referer here with the correct links. 
	req = urllib.request.Request(url='<url to run api endpoint>', data=data, method='POST')
	req.add_header('Cookie', cookie)
	req.add_header('User-Agent', agent)
	req.add_header('Content-Type', 'application/json')
	req.add_header('X-CSRFToken', csrftoken) # For some reason the csrftoken needs to be both here and in the Cookie.
	req.add_header('Referer', '<url to admin section of tracker>')
	
	# If you're still on the version of the tracker that takes form input instead of json, comment out the above lines from "data =" to here and uncomment the below docstring. Remember to replace the url to your run api endpoint.
	"""
	qstr = urllib.parse.urlencode(query)
	data = bytearray(qstr, 'utf-8')

	req = urllib.request.Request(url='<url to run api endpoint>', data=data, method='POST')
	req.add_header('Cookie', cookie)
	req.add_header('User-Agent', agent)
	"""

	try:
		with urllib.request.urlopen(req) as f:
			res = json.loads(f.read().decode('utf-8'))
	except urllib.request.HTTPError as e:
		print(f"Status code: {e.code}")
		print(f"Error: {e.file.read()}\nInput: {data}")

# This block is used to check Run Names against the Twitch game directory list. If they do not exist, they'll be added to the text file at the bottom.
# If you skipped the step where a twitch oauth key was obtained at the start of this file, comment this code out.
for run in runs:

	name = run[4].strip()

	req = urllib.request.Request(url="https://api.twitch.tv/helix/games?name={0}".format(urllib.parse.quote(name)))
	req.add_header('Client-ID', cid)
	req.add_header('Authorization', 'Bearer '+oauth)
	
	try:
		with urllib.request.urlopen(req) as f:
			response = json.loads(f.read().decode('UTF-8'))
			if not response['data']:
				responselist.append(name+': Does Not Exist as a Twitch Directory')
				print(name+': Does Not Exist as a Twitch Directory')
			else:
				print(name+': Exists as a Twitch Directory')
	except urllib.request.HTTPError as e:
		print(e.file.read(), urllib.parse.quote(name))	

with open('<filename>','w',encoding='utf-8') as f:
	for x in responselist:
		f.write(x+'\n')