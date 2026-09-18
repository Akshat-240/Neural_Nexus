import os
import json
import urllib.request
import urllib.error
import uuid
import logging
import ssl
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AzureTranslatorAdapter:
    def __init__(self):
        self.key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
        self.endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    
    def translate_text(self, text: str, target_lang: str) -> Dict[str, Any]:
        """
        Translates text to target_lang using Azure Translator API.
        """
        if not text:
            return {"translated_text": text, "source_language": "unknown", "error": "Missing text"}

        if not self.key:
            logger.info("Azure Translator not configured - using mock translation")
            # Specific mocks for demo scenarios
            if target_lang == "hi":
                if "24-XX spool erected today at Unit 3" in text:
                    mock_text = "यूनिट 3 पर आज 24-XX स्पूल स्थापित किया गया।"
                elif "Line 24 work completed" in text:
                    mock_text = "लाइन 24 का काम पूरा हो गया।"
                elif "Pipe support installation is approximately 50 percent complete at Unit 3" in text:
                    mock_text = "यूनिट 3 में पाइप सपोर्ट इंस्टॉलेशन लगभग 50 प्रतिशत पूरा हो गया है।"
                else:
                    mock_text = f"[अनुवादित (Hindi)]: {text}"
            else:
                mock_text = f"[Translated to {target_lang}]: {text}"

            return {
                "translated_text": mock_text,
                "source_language": "en",
                "target_lang": target_lang
            }

        # API version and target language parameter
        url = f"{self.endpoint}?api-version=3.0&to={target_lang}"

        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.region,
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
                if isinstance(result, list) and len(result) > 0:
                    translation = result[0].get("translations", [{}])[0].get("text", "")
                    detected_lang = result[0].get("detectedLanguage", {}).get("language", "en")
                    return {
                        "translated_text": translation,
                        "source_language": detected_lang,
                        "target_lang": target_lang
                    }
                return {"translated_text": text, "error": "Invalid format returned"}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"Translator HTTP Error {e.code}: {error_body}")
            return {"translated_text": text, "error": f"HTTP {e.code}"}
        except Exception as e:
            logger.error(f"Translator Exception: {e}")
            return {"translated_text": text, "error": str(e)}
