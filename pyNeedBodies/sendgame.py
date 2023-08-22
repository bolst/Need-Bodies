import requests

headers = {'Content-Type': 'application/json'}

r = requests.post('http://127.0.0.1:5000/addGame/0/nic bolt/20/2',
                  headers=headers,
                  json={
                      'date': '20190113',
                      'time': '1200',
                      'location': 'Central Park Athletics (formerly Ice Park Arena)'
                  })

print(r.status_code, '-', r.content)
