import requests

requests.get('http://127.0.0.1:8000/quote', params={
    'vocab': 'hello'
})
