"""
AWS Bedrock Service for generating responses using foundation models.
This service provides a simple interface to invoke Bedrock Runtime
for a demo chatbot application.
"""

import os
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
        Generate a response using Amazon Nova Lite.
        """

        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")

            import json
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": question
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 2000,
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

            response_body = response["body"].read().decode("utf-8")
            result = json.loads(response_body)

            # Extract the text content safely
            try:
                text_content = result["output"]["message"]["content"][0]["text"]
                # Log if response seems truncated
                if len(text_content) >= 1900:  # Close to our token limit
                    print(f"Warning: Response approaching token limit ({len(text_content)} characters)")
                return text_content
            except (KeyError, IndexError) as e:
                # Fallback for different response formats
                if "completion" in result:
                    return result["completion"]
                elif "outputText" in result:
                    return result["outputText"]
                else:
                    print(f"Unexpected response format: {result}")
                    return str(result)

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
                
        except ClientError as e:
            # Handle AWS service-specific errors
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", "AWS service error")
            raise Exception(f"AWS Bedrock error ({error_code}): {error_msg}")
            
        except BotoCoreError as e:
            # Handle AWS SDK core errors
            raise Exception(f"AWS SDK error: {str(e)}")
            
        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            raise Exception(f"Failed to parse Bedrock response: {str(e)}")
            
        except Exception as e:
            # Handle any other unexpected errors
            raise Exception(f"Failed to generate response: {str(e)}")


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