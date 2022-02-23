import requests

url = "http://0.0.0.0:1234/lctl_get_param"

r = requests.post(url, json={"path": "obdfilter.*.stats"})
print(r.json())
