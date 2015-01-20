import os

FILES = ".deepblue.password"

keys = {}

if os.path.exists(FILES):
	for line in open(FILES).readlines():
		print line
		(project, user, password) = line.split(":", 3)
		keys[project] = (user.strip(), password.strip())


def PROJECT_USER(project):
	if keys.has_key(project):
		return keys[project][0]
	return ""

def PROJECT_PASSWORD(project):
	if keys.has_key(project):
		return keys[project][1]
	return ""
