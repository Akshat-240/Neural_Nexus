import os
import json
import urllib.request
import urllib.error
import uuid
import ssl

key = "YOUR_API_KEY"
region = "eastus"
endpoint = "https://api.cognitive.microsofttranslator.com/translate"

text = "Hello world"
target_lang = "hi"

url = f"{endpoint}?api-version=3.0&to={target_lang}"
headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': region,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}
body = json.dumps([{"text": text}]).encode('utf-8')

req = urllib.request.Request(url, data=body, headers=headers, method='POST')

try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("SUCCESS:")
        print(json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"EXCEPTION: {e}")
