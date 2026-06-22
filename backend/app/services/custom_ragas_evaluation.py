from typing import List, Dict, Any, Optional
from app.services.embedding_service import EmbeddingService
import boto3
import json
# from datasets import Dataset
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CustomRagasEvaluationService:
    """
    Custom RAGAS evaluation service using Nova Lite as judge
    Avoids problematic dependencies while providing semantic evaluation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Use boto3 directly for Nova Lite judge (avoids langchain-aws dependency)
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1"
        )
        self.judge_model_id = "amazon.nova-lite-v1:0"
        
        # Use existing embedding service
        self.embedding_service = EmbeddingService()
        
        self.logger.info("Custom RAGAS evaluation service initialized with Nova Lite judge")
    
    def _invoke_nova_lite(self, prompt: str) -> str:
        """Invoke Nova Lite model directly using boto3 with correct format"""
        try:
            # Use the correct Bedrock Converse API format for Nova Lite
            response = self.bedrock_runtime.invoke_model(
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }),
                modelId=self.judge_model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            result = json.loads(response.get("body").read())
            
            # Debug: Print the actual response structure
            self.logger.debug(f"Nova Lite raw response: {result}")
            
            # Extract score from the response
            score_text = ""
            try:
                # Try new Bedrock Converse API format
                if "output" in result and "message" in result["output"]:
                    content = result["output"]["message"].get("content", [])
                    if content and isinstance(content, list):
                        score_text = content[0].get("text", "")
                # Try older format
                elif "message" in result:
                    content = result["message"].get("content", [])
                    if content and isinstance(content, list):
                        score_text = content[0].get("text", "")
                
                # Extract just the number if Nova added explanation
                import re
                match = re.search(r'\d*\.?\d+', score_text)
                if match:
                    return match.group(0)
                else:
                    return score_text
                    
            except Exception as parse_error:
                self.logger.warning(f"Failed to parse Nova Lite response: {parse_error}")
                return ""
                
        except Exception as e:
            self.logger.warning(f"Nova Lite invocation failed (using fallback): {e}")
            return ""
    
    def evaluate_rag_response(self, 
                           question: str, 
                           answer: str, 
                           context: str, 
                           ground_truth: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a single RAG response using custom RAGAS metrics with Nova Lite judge
        
        Args:
            question: The user's question
            answer: The generated answer
            context: The retrieved context used to generate the answer
            ground_truth: Optional ground truth answer for comparison
        
        Returns:
            Dictionary containing evaluation metrics and scores
        """
        try:
            # Calculate all metrics
            faithfulness = self._calculate_faithfulness_with_llm(answer, context)
            answer_relevancy = self._calculate_answer_relevancy_with_llm(question, answer)
            context_precision = self._calculate_context_precision_with_embeddings(context, question)
            context_recall = self._calculate_context_recall_with_embeddings(context, question)
            context_relevancy = self._calculate_context_relevancy_with_llm(context, question)
            
            overall_score = (faithfulness + answer_relevancy + context_precision + 
                           context_recall + context_relevancy) / 5.0
            
            evaluation_result = {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "context_relevancy": context_relevancy,
                "overall_score": overall_score,
                "evaluation_method": "custom_ragas_nova_lite"
            }
            
            self.logger.info(f"Custom RAGAS Evaluation Results: {evaluation_result}")
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Error in custom RAGAS evaluation: {e}")
            return {
                "error": str(e),
                "faithfulness": 0.0,
                "answer_relevancy": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "context_relevancy": 0.0,
                "overall_score": 0.0,
                "evaluation_method": "error"
            }
    
    def _calculate_faithfulness_with_llm(self, answer: str, context: str) -> float:
        """Calculate faithfulness using Nova Lite as judge"""
        prompt = f"""Evaluate whether the answer is faithfully supported by the context.
        
Context: {context}
Answer: {answer}

Score the faithfulness on a scale from 0 to 1, where:
0 = Answer contains hallucinations or unsupported claims
0.5 = Answer is partially supported by context
1 = Answer is completely and accurately supported by context

Provide ONLY the numeric score (e.g., "0.8"), nothing else:"""
        
        try:
            response_text = self._invoke_nova_lite(prompt)
            if not response_text:
                raise ValueError("Empty response from Nova Lite")
            
            score_str = response_text.strip()
            score = min(1.0, max(0.0, float(score_str)))
            print(f"[NOVA LITE JUDGE] Faithfulness score: {score}")  # Force console output
            return score
        except Exception as e:
            print(f"[FALLBACK] LLM faithfulness evaluation failed: {e}")  # Force console output
            fallback_score = self._calculate_text_overlap_faithfulness(answer, context)
            print(f"[FALLBACK] Using text overlap score: {fallback_score}")  # Force console output
            return fallback_score
    
    def _calculate_answer_relevancy_with_llm(self, question: str, answer: str) -> float:
        """Calculate answer relevancy using Nova Lite as judge"""
        prompt = f"""Evaluate how well the answer addresses the question.
        
Question: {question}
Answer: {answer}

Score the answer relevancy on a scale from 0 to 1, where:
0 = Answer is completely irrelevant to the question
0.5 = Answer is partially relevant but misses key aspects
1 = Answer directly and completely addresses the question

Provide ONLY the numeric score (e.g., "0.8"), nothing else:"""
        
        try:
            response_text = self._invoke_nova_lite(prompt)
            if not response_text:
                raise ValueError("Empty response from Nova Lite")
            
            score_str = response_text.strip()
            score = min(1.0, max(0.0, float(score_str)))
            print(f"[NOVA LITE JUDGE] Answer relevancy score: {score}")
            return score
        except Exception as e:
            print(f"[FALLBACK] LLM relevancy evaluation failed: {e}")
            fallback_score = self._calculate_text_overlap_relevancy(question, answer)
            print(f"[FALLBACK] Using text overlap score: {fallback_score}")
            return fallback_score
    
    def _calculate_context_precision_with_embeddings(self, context: str, question: str) -> float:
        """Calculate context precision using semantic similarity"""
        try:
            # Get embeddings
            context_embedding = self.embedding_service.generate_embedding(context)
            question_embedding = self.embedding_service.generate_embedding(question)
            
            if not context_embedding or not question_embedding:
                return 0.0
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [context_embedding], 
                [question_embedding]
            )[0][0]
            
            # Normalize to 0-1 range
            return min(1.0, max(0.0, similarity))
        except Exception as e:
            self.logger.warning(f"Embedding precision calculation failed: {e}")
            return self._calculate_text_overlap_precision(context, question)
    
    def _calculate_context_recall_with_embeddings(self, context: str, question: str) -> float:
        """Calculate context recall using semantic similarity"""
        # For recall, we use the same approach as precision in this simplified version
        return self._calculate_context_precision_with_embeddings(context, question)
    
    def _calculate_context_relevancy_with_llm(self, context: str, question: str) -> float:
        """Calculate context relevancy using Nova Lite as judge"""
        prompt = f"""Evaluate how relevant the context is to the question.
        
Question: {question}
Context: {context}

Score the context relevancy on a scale from 0 to 1, where:
0 = Context is completely irrelevant to the question
0.5 = Context is partially relevant but misses key information
1 = Context is highly relevant and directly addresses the question

Provide ONLY the numeric score (e.g., "0.8"), nothing else:"""
        
        try:
            response_text = self._invoke_nova_lite(prompt)
            if not response_text:
                raise ValueError("Empty response from Nova Lite")
            
            score_str = response_text.strip()
            score = min(1.0, max(0.0, float(score_str)))
            print(f"[NOVA LITE JUDGE] Context relevancy score: {score}")
            return score
        except Exception as e:
            print(f"[FALLBACK] LLM relevancy evaluation failed: {e}")
            fallback_score = self._calculate_text_overlap_relevancy(question, context)
            print(f"[FALLBACK] Using text overlap score: {fallback_score}")
            return fallback_score
    
    # Fallback methods using text overlap
    def _calculate_text_overlap_faithfulness(self, answer: str, context: str) -> float:
        """Fallback: Calculate faithfulness using text overlap"""
        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())
        
        if not answer_words:
            return 0.0
        
        overlap = len(answer_words.intersection(context_words))
        return min(1.0, overlap / len(answer_words))
    
    def _calculate_text_overlap_relevancy(self, text1: str, text2: str) -> float:
        """Fallback: Calculate relevancy using text overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1.intersection(words2))
        return min(1.0, overlap / len(words1))
    
    def _calculate_text_overlap_precision(self, context: str, question: str) -> float:
        """Fallback: Calculate precision using text overlap"""
        question_words = set(question.lower().split())
        context_words = set(context.lower().split())
        
        if not question_words:
            return 0.0
        
        relevant_words = len(question_words.intersection(context_words))
        return min(1.0, relevant_words / len(question_words))
    
    def evaluate_batch_responses(self, 
                                questions: List[str], 
                                answers: List[str], 
                                contexts: List[str], 
                                ground_truths: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Evaluate multiple RAG responses in batch
        
        Args:
            questions: List of user questions
            answers: List of generated answers
            contexts: List of retrieved contexts
            ground_truths: Optional list of ground truth answers
        
        Returns:
            List of evaluation results for each response
        """
        if len(questions) != len(answers) or len(questions) != len(contexts):
            raise ValueError("Questions, answers, and contexts must have the same length")
        
        if ground_truths and len(questions) != len(ground_truths):
            raise ValueError("Ground truths must have the same length as questions")
        
        results = []
        for i, (question, answer, context) in enumerate(zip(questions, answers, contexts)):
            ground_truth = ground_truths[i] if ground_truths else None
            evaluation = self.evaluate_rag_response(question, answer, context, ground_truth)
            results.append(evaluation)
        
        return results
    
    def generate_evaluation_report(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary report from multiple evaluations
        
        Args:
            evaluations: List of individual evaluation results
        
        Returns:
            Summary statistics and analysis
        """
        if not evaluations:
            return {"error": "No evaluations provided"}
        
        # Calculate averages
        avg_metrics = {}
        for metric in ["faithfulness", "answer_relevancy", "context_precision", 
                      "context_recall", "context_relevancy", "overall_score"]:
            values = [eval[metric] for eval in evaluations if metric in eval]
            avg_metrics[metric] = sum(values) / len(values) if values else 0.0
        
        # Identify potential issues with appropriate thresholds
        issues = []
        if avg_metrics["faithfulness"] < 0.75:
            issues.append("Low faithfulness - answers may contain unsupported claims or hallucinations")
        if avg_metrics["answer_relevancy"] < 0.70:
            issues.append("Low answer relevancy - answers may not directly address user questions")
        if avg_metrics["context_recall"] < 0.65:
            issues.append("Low context recall - retrieval may miss important relevant information")
        if avg_metrics["context_precision"] < 0.60:
            issues.append("Low context precision - retrieved context may contain irrelevant information")
        
        return {
            "average_metrics": avg_metrics,
            "total_evaluations": len(evaluations),
            "evaluation_method": evaluations[0].get("evaluation_method", "unknown") if evaluations else "unknown",
            "potential_issues": issues,
            "recommendations": self._generate_recommendations(avg_metrics)
        }
    
    def _generate_recommendations(self, avg_metrics: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on metrics"""
        recommendations = []
        
        if avg_metrics["faithfulness"] < 0.75:
            recommendations.append("Improve answer generation to reduce hallucinations - ensure answers are strictly grounded in retrieved context")
            recommendations.append("Add explicit instructions in prompt to only use provided context and avoid speculation")
        
        if avg_metrics["answer_relevancy"] < 0.70:
            recommendations.append("Enhance prompt engineering to ensure answers directly and completely address the user's question")
            recommendations.append("Consider adding question analysis or rephrasing steps before answer generation")
        
        if avg_metrics["context_recall"] < 0.65:
            recommendations.append("Adjust retrieval parameters: increase k (number of chunks) or lower confidence threshold to capture more relevant context")
            recommendations.append("Improve document chunking strategy to ensure comprehensive coverage of topics")
        
        if avg_metrics["context_precision"] < 0.60:
            recommendations.append("Improve embedding quality or implement better filtering to reduce irrelevant context retrieval")
            recommendations.append("Consider implementing query expansion or re-ranking to improve context relevance")
        
        if all(metric > 0.80 for metric in [avg_metrics["faithfulness"], avg_metrics["answer_relevancy"]]):
            recommendations.append("Excellent answer quality - focus on expanding knowledge base and handling edge cases")
        
        if not recommendations:
            recommendations.append("Overall strong performance - continue monitoring and consider user feedback for fine-tuning")
        
        return recommendations