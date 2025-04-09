import csv
import json
import urllib.request

csrf = b'' # Value of csrftoken=
cookie = b"tracker_session=<>; csrftoken=<>"

agent = b'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0' # Generic browser agent

incentives = []
ids = []
event = 0 # Replace with numeric id of event

# Replace filename with incentive sheet
with open('<filename>', 'r', encoding='utf-8') as f:
	r = csv.reader(f)
	for row in r:
		incentives.append(row)

# Cut off header row
incentives = incentives[1:]		


# Incentive Spreadsheet Format
# 0 - Ordered index of incentives, used for chain parent references
# 1 - Game ID to Attach To
# 2 - Game Name
# 3 - Incentive Name
# 4 - Incentive Description
# 5 - Incentive ShortDescription
# 6 - Incentive Type (goal, bidwar, submit)
#		goal: Has a goal donation value to hit.
#		bidwar: Choose between a number of preset options.
#		stretchparent: If this incentive is the parent of an incentive chain. (called stretch goals)
#		stretchchild: If this incentive is a child incentive attached to an incentive chain.
#		submit: Donators submit their own choices. Used for names.
#		milestone: Incentive is enabled once the total donations for the event reach this value.
# 7 - Incentive Time Length
# 8 - Incentive Close Time relative to Run
# 9 - Incentive Post-Run Status
# 10 - Reference to the ordered incentive list for chain incentive children to refer to parent incentives
# 11 - Incentive/Milestone Goal
# 12 - Incentive Option Count
# 13 - Incentive Max Length for User Suggestions
# 14 through 31 Even Values - Incentive Options
# 15 through 32 Odd Values - Incentive Short Descriptions

# Milestones use a different flow

for incentive in incentives:

	bidtype = 'bid'
	istarget = 'False'
	issubmit = 'False'
	ismilestone = 'False'
	ischain = 'False'
	postrun = 'False'
	addtime = ''
	maxlength = incentive[13]
	parent = incentive[10]
	
	if incentive[6].rstrip() == 'goal':
		istarget = 'True'
		
	if incentive[6].rstrip() == 'submit':
		issubmit = 'True'
	
	if incentive[6].rstrip() == 'milestone':
		ismilestone = 'True'
		bidtype = 'milestone'
		
	if incentive[6].rstrip() == 'stretchparent' or incentive[6].rstrip() == 'stretchchild':
		ischain = 'True'
		istarget = 'True'
		
	if incentive[9].rstrip() == 'Yes':
		postrun = 'True'
		
	if incentive[7].rstrip() != '0:00:00' and incentive[7].rstrip() != "":
		addtime = incentive[7].rstrip()
		
	if bidtype == 'bid':
		
		query = {
			'name': incentive[3].rstrip(),
			'description': incentive[4].rstrip(),
			'shortdescription': incentive[5].rstrip(),
			'goal': incentive[11],
			'chain': ischain
		}
		
		if incentive[6].rstrip() != 'stretchchild':
		
			query.update(
			{
				'state': 'HIDDEN',
				'istarget': istarget,
				'speedrun': incentive[1],
				'allowuseroptions': issubmit,
				'estimate': addtime,
				'close_at': incentive[8].rstrip(),
				'post_run': postrun
			}
			)
		
		if incentive[6].rstrip() == 'stretchchild':
			
			parent = int(incentive[10].rstrip())
			query.update(
			{
				'parent': ids[parent-1],
				'istarget': 'False'
			}
			)
		
		if maxlength != "":
		
			query.update(
			{
				'option_max_length': maxlength
			}
			)
			
			
		data = json.dumps(query).encode('utf-8')
		
		req = urllib.request.Request(url='<url to bids endpoint>', data=data, method='POST')
		req.add_header('Cookie', cookie)
		req.add_header('User-Agent', agent)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		req.add_header('Referer', '<url to admin site>')
		req.add_header('X-CSRFToken', csrf)

		try:
			with urllib.request.urlopen(req) as f:
				res = json.loads(f.read().decode('utf-8'))
				print(res)
				rid = res['id']
				ids.append(rid)
		except urllib.request.HTTPError as e:
			print(e.file.read(), data)
			ids.append(0)
	
	# milestones have a different endpoint
	elif bidtype == 'milestone':
		query = {
			'event': event,
			'type': 'milestone',
			'name': incentive[3].rstrip(),
			'run': incentive[1].rstrip(),
			'visible': 'False',
			'description': incentive[4].rstrip(),
			'short_description': incentive[5].rstrip(),
			'amount': incentive[11]
		}
	
		jsondata = json.dumps(query)
		data = jsondata.encode('utf-8')

		req = urllib.request.Request(url='<url to milestone endpoint>', data=data, method='POST')
		req.add_header('Cookie', cookie)
		req.add_header('User-Agent', agent)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		req.add_header('X-CSRFToken', csrf)
		req.add_header('Referer', '<url to admin site>')
		
		try:
			with urllib.request.urlopen(req) as f:
				res = json.loads(f.read().decode('utf-8'))
				print(res)
				rid = res['id']
				ids.append(rid)
		except urllib.request.HTTPError as e:
			print(e.file.read(), data)
			ids.append(0)

		
for incentive in incentives:

	this = ids[0]
	ids = ids[1:]
	if not this:
		continue
		
	hasoptions = incentive[12]
	if not hasoptions:
		continue
		
	query = {
		'type': 'bid',
		'parent': this,
		'state': 'HIDDEN',
		'istarget': 'True',
		'event': event
	}
	
	for i in range(int(hasoptions)):
		query.update(
		{
			'name': incentive[14+(2*i)].rstrip(),
			'shortdescription': incentive[15+(2*i)+1].rstrip()
		}
		)

		# v2 API method
		data = json.dumps(query).encode('utf-8')
	
		req = urllib.request.Request(url='<url to bids endpoint>', data=data, method='POST')
		req.add_header('Cookie', cookie)
		req.add_header('User-Agent', agent)
		req.add_header('Content-Type', 'application/json; charset=utf-8')
		req.add_header('Referer', '<url to admin site>')
		req.add_header('X-CSRFToken', csrf)

		try:
			with urllib.request.urlopen(req) as f:
				print(f.read())
		except urllib.request.HTTPError as e:
			print(e.file.read(), data)
		
