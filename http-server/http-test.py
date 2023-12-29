import requests
import json


def test_create_genesis_branch():
    url = "http://localhost:3356/create_genesis_branch"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "branch_type": 1,
        "signature": "0x1234567890",
        "accept_conflicts": True,
        "msg": "Hello, World!"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Test the create_genesis_branch route
response = test_create_genesis_branch()
print(response)
