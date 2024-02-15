import json

import requests

def query_rasa(instruction):
    payload = {"sender": "Rasa", "text": instruction}
    headers = {'content-type': 'application/json'}
    # response = requests.post('http://localhost:5005/model/parse', json=payload, headers=headers)
    response = requests.post('http://localhost:5005/model/parse', data=json.dumps({'text':instruction}))
    # response = requests.post('http://rasaserv:5005/model/parse', data=json.dumps({'text':instruction}))
    result = response.json()
    return result

# instruction = "pour water into bottle from the bowl"
# payload = {"sender": "Rasa", "text": instruction}
# headers = {'content-type': 'application/json'}
# # response = requests.post('http://localhost:5005/model/parse', json=payload, headers=headers)
# response = requests.post('http://localhost:5005/model/parse', data=json.dumps({'text':instruction}))
# result = response.json()
# print(result)