import json
import urllib.request
import urllib.error
import uuid
import ssl

key = "YOUR_API_KEY"
endpoint = "https://api.cognitive.microsofttranslator.com/translate"
text = "Hello"
target_lang = "hi"
url = f"{endpoint}?api-version=3.0&to={target_lang}"

regions = ["eastus", "eastus2", "centralus", "westus", "westus2", "centralindia", "southindia", "westeurope", "northeurope", "southeastasia", "uksouth", "australiaeast", "global", ""]

for region in regions:
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    if region:
        headers['Ocp-Apim-Subscription-Region'] = region
        
    body = json.dumps([{"text": text}]).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"SUCCESS with region: {region}")
            break
    except urllib.error.HTTPError as e:
        # print(f"Failed {region}: {e.code}")
        pass
    except Exception as e:
        pass
