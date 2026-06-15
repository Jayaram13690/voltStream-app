#!/usr/bin/env python

"""
Simple script to demonstrate RAGAS evaluation using the custom implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("RAGAS Evaluation Demo")
    print("=" * 50)
    
    try:
        from app.services.custom_ragas_evaluation import CustomRagasEvaluationService
        
        # Initialize the evaluation service
        evaluator = CustomRagasEvaluationService()
        
        # Sample test case
        question = "What are the main advantages of renewable energy?"
        context = "Renewable energy sources like solar and wind power are sustainable, reduce greenhouse gas emissions, and can lower energy costs in the long run. They also decrease dependence on fossil fuels."
        answer = "The main advantages of renewable energy include sustainability, reduced greenhouse gas emissions, lower long-term energy costs, and decreased dependence on fossil fuels."
        
        print(f"\nQuestion: {question}")
        print(f"Context: {context}")
        print(f"Answer: {answer}")
        print("\nEvaluating with Custom RAGAS (Nova Lite Judge)...")
        
        # Perform evaluation
        evaluation = evaluator.evaluate_rag_response(question, answer, context)
        
        print("\n" + "=" * 50)
        print("RAGAS Evaluation Results:")
        print("=" * 50)
        print(f"Faithfulness:        {evaluation.get('faithfulness', 'N/A'):.3f}")
        print(f"Answer Relevancy:    {evaluation.get('answer_relevancy', 'N/A'):.3f}")
        print(f"Context Precision:   {evaluation.get('context_precision', 'N/A'):.3f}")
        print(f"Context Recall:      {evaluation.get('context_recall', 'N/A'):.3f}")
        print(f"Context Relevancy:   {evaluation.get('context_relevancy', 'N/A'):.3f}")
        print(f"Overall Score:       {evaluation.get('overall_score', 'N/A'):.3f}")
        print(f"Evaluation Method:   {evaluation.get('evaluation_method', 'N/A')}")
        
        # Generate report
        report = evaluator.generate_evaluation_report([evaluation])
        
        print(f"\n" + "=" * 50)
        print("Evaluation Summary:")
        print("=" * 50)
        print(f"Average Score: {report['average_metrics']['overall_score']:.3f}/1.0")
        
        if report['potential_issues']:
            print(f"\nPotential Issues:")
            for issue in report['potential_issues']:
                print(f"  - {issue}")
        else:
            print("\nNo major issues detected!")
            
        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        print(f"\n[+] RAGAS evaluation completed successfully!")
        
    except ImportError as e:
        print(f"[-] Import error: {e}")
        print("Please ensure all dependencies are installed.")
    except Exception as e:
        print(f"[-] Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()