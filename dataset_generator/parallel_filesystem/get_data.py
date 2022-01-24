import requests

url = "http://0.0.0.0:1234/get_data"

r = requests.post(url, json={"path": "/sys/kernel/debug/dynamic_debug/control"})
print(r.json()["content"])
