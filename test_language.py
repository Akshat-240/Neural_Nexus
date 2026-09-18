from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

key = "YOUR_API_KEY"
endpoint = "https://neuralnexus.cognitiveservices.azure.com/"

client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
result = client.detect_language(documents=["Hello world"])
print(result[0].primary_language.name)
