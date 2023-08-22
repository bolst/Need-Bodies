import requests

headers = {'Content-Type': 'application/json'}

r = requests.get('http://127.0.0.1:5000/addUserToGame/0/1/no')

print(r.status_code, '-', r.content)
