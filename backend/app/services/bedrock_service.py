"""
AWS Bedrock Service for generating responses using foundation models.
This service provides a simple interface to invoke Bedrock Runtime
for a demo chatbot application.
"""

import os
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Optional
from dotenv import load_dotenv
from app.core.config import get_settings

# Load environment variables from .env file
load_dotenv()


class BedrockService:
    """
    Service class for interacting with AWS Bedrock Runtime.
    
    Attributes:
        region (str): AWS region for Bedrock service
        model_id (str): Bedrock foundation model ID
        client: Bedrock Runtime client
    """
    
    def __init__(self):
        """
        Initialize the Bedrock service with configuration from application settings.
        
        Uses the application's configuration system which loads from .env file.
        """
        # Get configuration from application settings
        settings = get_settings()
        
        self.region = settings.aws_region
        self.model_id = settings.bedrock_model_id
        
        if not self.model_id:
            raise ValueError(
                "BEDROCK_MODEL_ID is not configured. "
                "Please set it in your .env file."
            )
        
        # Initialize Bedrock Runtime client
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
    
    def generate_response(self, question: str) -> str:
        """
        Generate response using prompt engineering for complete answers.
        Uses structured prompts to ensure responses are well-formed and complete.
        """

        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")

            # Use prompt engineering to ensure complete responses
            structured_prompt = self._build_structured_prompt(question)

            response = self._generate_with_tokens(structured_prompt, 500)
            return response

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", "AWS service error")
            raise Exception(
                f"AWS Bedrock error ({error_code}): {error_msg}"
            )

        except BotoCoreError as e:
            raise Exception(f"AWS SDK error: {str(e)}")

        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    def generate_rag_response(self, rag_prompt: str) -> str:
        """Generate response using RAG prompt without modification"""
        return self._generate_with_tokens(rag_prompt, 1000)
    
    def _generate_with_tokens(self, prompt: str, token_limit: int) -> str:
        """Generate response with specific token limit"""
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": token_limit,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read().decode("utf-8"))
        
        # Extract the text content safely
        try:
            return result["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError):
            # Fallback for different response formats
            if "completion" in result:
                return result["completion"]
            elif "outputText" in result:
                return result["outputText"]
            else:
                print(f"Unexpected response format: {result}")
                return str(result)
    
    def _build_structured_prompt(self, question: str) -> str:
        """Build a context-aware prompt that handles different question types appropriately"""
        
        # Detect question type and adjust prompt accordingly
        question_lower = question.lower().strip()

        # Handle greetings and simple conversations
        if any(greeting in question_lower for greeting in ['hi', 'hello', 'hey', 'how are you']):
            return f"""
            You are VoltStream AI Assistant. The user greeted you with: '{question}'
            Respond with a friendly greeting and briefly mention you can help with energy-related questions.
            Keep the response warm and concise (under 50 words).
            """

        # Handle energy/solar specific questions
        elif any(topic in question_lower for topic in ['energy', 'solar', 'power', 'electricity', 'renewable', 'sustainability', 'battery', 'grid']):
            return f"""
            You are VoltStream AI Assistant, an expert in energy, solar systems, and sustainability.
            Provide a complete, well-structured answer to the following question.
            Your response should:

            1. Start with a clear, concise definition or explanation
            2. Include 2-3 key points with examples where relevant
            3. End with a summary sentence or conclusion
            4. Use bullet points for lists
            5. Keep the total response under 400 words

            Question: {question}

            Format your response as follows:
            [Brief introduction]

            Key points:
            • Point 1 with brief explanation
            • Point 2 with brief explanation
            • Point 3 with brief explanation (if applicable)

            [Concluding sentence that summarizes the main takeaway]
            """

        # Handle general questions
        else:
            return f"""
            You are VoltStream AI Assistant.
            Answer the following general question concisely and helpfully.

            Question: {question}

            Guidelines:
            1. Be helpful and professional
            2. Keep responses under 300 words
            3. Always maintain a friendly, helpful tone
            """


def get_bedrock_service() -> BedrockService:
    """
    Factory function to create and return a BedrockService instance.
    Returns:
        BedrockService: Initialized Bedrock service instance
    """
    return BedrockService()


# Convenience function for direct usage
def generate_response(question: str) -> str:
    """
    Convenience function to generate a response using Bedrock.
    
    This function creates a BedrockService instance and generates
    a response to the provided question.
    
    Args:
        question (str): The input question or prompt
        
    Returns:
        str: The generated response text
        
    Example:
        >>> response = generate_response("What is solar energy?")
        >>> print(response)
    """
    service = get_bedrock_service()
    return service.generate_response(question)