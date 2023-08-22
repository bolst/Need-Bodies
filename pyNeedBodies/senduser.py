import requests

headers = {'Content-Type': 'application/json'}

r = requests.post('http://127.0.0.1:5000/addUser/nic bolton/5198176511',
                  headers=headers,
                  json={
                      'email': 'nicbolton10@icloud.com',
                      'password': '1234',
                  })

print(r.status_code, '-', r.content)