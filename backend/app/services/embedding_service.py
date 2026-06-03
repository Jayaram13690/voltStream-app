import boto3
from typing import List
import json

class EmbeddingService:
    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0"):
        self.model_id = model_id
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1"
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Amazon Titan Text Embeddings V2"""
        try:
            response = self.bedrock_runtime.invoke_model(
                body=json.dumps({
                    "inputText": text
                }),
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            result = json.loads(response.get("body").read())
            return result.get("embedding", [])
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []