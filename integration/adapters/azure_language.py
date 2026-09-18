import os
import logging
from typing import Dict, Any

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

logger = logging.getLogger(__name__)

class AzureLanguageAdapter:
    def __init__(self):
        self.key = os.getenv("AZURE_LANGUAGE_KEY")
        self.endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
        self.client = None

        if self.key and self.endpoint:
            try:
                self.client = TextAnalyticsClient(
                    endpoint=self.endpoint, 
                    credential=AzureKeyCredential(self.key)
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure TextAnalyticsClient: {e}")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the text for language, sentiment, key phrases, and entities.
        """
        if not text or not self.client:
            return {}

        results = {
            "language": None,
            "sentiment": None,
            "key_phrases": [],
            "entities": []
        }

        documents = [text]

        try:
            # 1. Language Detection
            lang_response = self.client.detect_language(documents=documents)[0]
            if not lang_response.is_error:
                results["language"] = {
                    "name": lang_response.primary_language.name,
                    "iso6391_name": lang_response.primary_language.iso6391_name,
                    "confidence": lang_response.primary_language.confidence_score
                }

            # 2. Sentiment Analysis
            sent_response = self.client.analyze_sentiment(documents=documents)[0]
            if not sent_response.is_error:
                results["sentiment"] = {
                    "overall": sent_response.sentiment,
                    "positive_score": sent_response.confidence_scores.positive,
                    "neutral_score": sent_response.confidence_scores.neutral,
                    "negative_score": sent_response.confidence_scores.negative,
                }

            # 3. Key Phrases
            phrase_response = self.client.extract_key_phrases(documents=documents)[0]
            if not phrase_response.is_error:
                results["key_phrases"] = phrase_response.key_phrases

            # 4. Entity Recognition
            entity_response = self.client.recognize_entities(documents=documents)[0]
            if not entity_response.is_error:
                results["entities"] = [
                    {"text": e.text, "category": e.category, "confidence": e.confidence_score}
                    for e in entity_response.entities
                ]

        except Exception as e:
            logger.error(f"Azure Language API error: {e}")

        return results
