import requests

headers = {'Content-Type': 'application/json'}

r = requests.post('http://127.0.0.1:5000/checkUser/0',
                  headers=headers,
                  json={
                      'password': 'Hockey1!'
                  })

print(r.status_code, '-', r.content)
