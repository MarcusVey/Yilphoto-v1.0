import json

with open("config.json", "r") as f:
	config = json.load(f)

print(config)

hosts = config[0]["hosts"]
paths = config[1]["paths"]
ports = config[2]["ports"]
users = config[3]["users"]

print(hosts['coils'])
print(paths['localpath'])
print(ports['ftp'])
print(users["username"])
print(users["password"])

for items in hosts.items():
	print(items)

for keys in hosts.keys():
	print(keys)

for values in hosts.values():
	print(values)