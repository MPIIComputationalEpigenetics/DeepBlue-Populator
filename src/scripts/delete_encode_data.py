import xmlrpclib

user_key = "NUI5O3YKJzi6XtEz"
url = "http://localhost:31415"
server = xmlrpclib.Server(url, encoding='UTF-8', allow_none=True)


def remove_biosource(biosource_id, name):
	print biosource_id, name
	status, subs = server.get_biosource_children(name, user_key)
	if status == 'error':
		return
	for sub in subs[1:]:
		print  "going to remove", str(sub)
		remove_biosource(sub[0], sub[1])

	for sample in server.list_samples(name, {}, user_key)[1]:
		print "listing samples: ", str(sample)
		for experiment in server.list_experiments ( None, None, sample[0], None, None, user_key )[1]:
			print "removing experiment", str(experiment)
			print server.remove(experiment[0], user_key)

		print server.remove(sample[0], user_key)

	print 'removing biosource', biosource_id, name
	print server.remove(biosource_id, user_key)


for bs in server.list_biosources(user_key)[1]:
	_id = bs[0]

	status, info = server.info(_id, user_key)
	if status == "okay":
		if info[0]['extra_metadata'].has_key("source") and info[0]['extra_metadata']["source"] == "ENCODE":
			print info[0]
			remove_biosource(_id, info[0]['name'])
	else:
		print info


	status, samples = server.list_samples(bs[1], {}, user_key)
	for sample in samples:
		if sample[1]["source"] != "ENCODE":
			continue
		print "listing samples: ", str(sample)
		for experiment in server.list_experiments ( None, None, sample[0], None, None, user_key )[1]:
			print "removing experiment", str(experiment)
			print server.remove(experiment[0], user_key)

		print server.remove(sample[0], user_key)


