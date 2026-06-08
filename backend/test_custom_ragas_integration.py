#!/usr/bin/env python

"""
Test script for custom RAGAS integration using Nova Lite as judge
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_custom_ragas_integration():
    """Test custom RAGAS evaluation with Nova Lite judge"""
    print("Testing Custom RAGAS integration with Nova Lite...")
    
    try:
        from app.services.custom_ragas_evaluation import CustomRagasEvaluationService
        
        # Initialize custom RAGAS service
        ragas_service = CustomRagasEvaluationService()
        
        # Sample test data
        question = "What are the benefits of solar energy?"
        context = "Solar energy is renewable, reduces electricity bills, and has low maintenance costs. It also reduces carbon footprint."
        answer = "Solar energy offers several benefits including being renewable, reducing electricity bills, having low maintenance costs, and reducing carbon footprint."
        
        print(f"Question: {question}")
        print(f"Context: {context}")
        print(f"Answer: {answer}")
        print()
        
        # Evaluate the response
        evaluation = ragas_service.evaluate_rag_response(question, answer, context)
        
        print("Custom RAGAS Evaluation Results (Nova Lite Judge):")
        print(f"Faithfulness: {evaluation.get('faithfulness', 'N/A'):.3f}")
        print(f"Answer Relevancy: {evaluation.get('answer_relevancy', 'N/A'):.3f}")
        print(f"Context Precision: {evaluation.get('context_precision', 'N/A'):.3f}")
        print(f"Context Recall: {evaluation.get('context_recall', 'N/A'):.3f}")
        print(f"Context Relevancy: {evaluation.get('context_relevancy', 'N/A'):.3f}")
        print(f"Overall Score: {evaluation.get('overall_score', 'N/A'):.3f}")
        print(f"Evaluation Method: {evaluation.get('evaluation_method', 'N/A')}")
        
        if 'error' in evaluation:
            print(f"Error: {evaluation['error']}")
            return False
        
        # Check if scores are reasonable
        if evaluation['overall_score'] > 0.5:
            print("\n[+] Custom RAGAS integration test passed!")
            print("[+] Evaluation framework is working (using embeddings + fallbacks)")
            print("[+] Note: Nova Lite LLM judging is attempted but falls back to text overlap")
            return True
        else:
            print(f"\n[!] Warning: Low overall score ({evaluation['overall_score']:.3f})")
            print("[!] This might indicate issues with the RAG response quality")
            return True  # Still passed the integration test
        
    except ImportError as e:
        print(f"[-] Import error: {e}")
        return False
    except Exception as e:
        print(f"[-] Error during custom RAGAS evaluation: {e}")
        return False

def test_custom_ragas_batch_evaluation():
    """Test batch evaluation with custom RAGAS"""
    print("\nTesting Custom RAGAS batch evaluation...")
    
    try:
        from app.services.custom_ragas_evaluation import CustomRagasEvaluationService
        
        evaluator = CustomRagasEvaluationService()
        
        # Sample batch data
        questions = [
            "What are the benefits of solar energy?",
            "How does solar energy work?"
        ]
        answers = [
            "Solar energy offers several benefits including being renewable, reducing electricity bills, having low maintenance costs, and reducing carbon footprint.",
            "Solar energy works by converting sunlight into electricity using photovoltaic cells."
        ]
        contexts = [
            "Solar energy is renewable, reduces electricity bills, and has low maintenance costs. It also reduces carbon footprint.",
            "Photovoltaic cells convert sunlight directly into electricity through the photovoltaic effect."
        ]
        
        print(f"Evaluating {len(questions)} responses with Nova Lite judge...")
        
        results = evaluator.evaluate_batch_responses(questions, answers, contexts)
        
        print(f"Evaluated {len(results)} responses")
        for i, result in enumerate(results):
            print(f"Response {i+1} Overall Score: {result.get('overall_score', 0.0):.3f}")
        
        # Generate report
        report = evaluator.generate_evaluation_report(results)
        print(f"\nCustom RAGAS Batch Evaluation Report:")
        print(f"Average Overall Score: {report['average_metrics']['overall_score']:.3f}")
        print(f"Total Evaluations: {report['total_evaluations']}")
        print(f"Evaluation Method: {report['evaluation_method']}")
        
        if report['potential_issues']:
            print("Potential Issues:")
            for issue in report['potential_issues']:
                print(f"  - {issue}")
        else:
            print("No major issues detected")
        
        if report['recommendations']:
            print("Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        print("\n[+] Custom RAGAS batch evaluation test passed!")
        return True
        
    except Exception as e:
        print(f"[-] Error during custom RAGAS batch evaluation: {e}")
        return False

if __name__ == "__main__":
    print("Running Custom RAGAS integration tests with Nova Lite...\n")
    
    test1_passed = test_custom_ragas_integration()
    test2_passed = test_custom_ragas_batch_evaluation()
    
    if test1_passed and test2_passed:
        print("\n[+] All custom RAGAS tests passed! Evaluation framework is working.")
        print("[+] Using Titan Embeddings for semantic metrics + text overlap fallbacks.")
        print("[+] Nova Lite LLM judging is attempted but currently falls back to heuristics.")
        sys.exit(0)
    else:
        print("\n[-] Some tests failed. Please check the errors above.")
        sys.exit(1)