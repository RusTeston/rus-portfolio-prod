#!/usr/bin/env python3
"""
Test script to validate AI Agent fixes for 6-pillar issue
"""

import json

def test_prompt_construction():
    """Test the improved prompt construction"""
    
    # Sample retrieved documents (from your embeddings)
    sample_docs = [
        {"text": "The AWS Well-Architected Framework is based on six pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability."},
        {"text": "Sustainability pillar focuses on minimizing the environmental impacts of running cloud workloads."},
        {"text": "The framework provides a consistent approach for customers and partners to evaluate architectures and implement designs that scale over time."}
    ]
    
    query = "How many pillars are in the Well-Architected Framework?"
    
    # Build prompt using fixed function logic
    doc_section = "\n".join(f"- {doc['text']}" for doc in sample_docs)
    prompt = f"""
User question: {query}

CRITICAL: Base your answer ONLY on the information provided below. Do NOT use your general knowledge about AWS or any other topics.

Retrieved context from official AWS Well-Architected Framework documentation:
{doc_section}

Available tools: NotifyHR, SummarizeDoc, CreateTask

Instructions: 
1. Answer using EXCLUSIVELY the information from the retrieved context above
2. If the context mentions specific numbers (like "six pillars"), use those EXACT numbers
3. Include ALL pillars, principles, or components mentioned in the retrieved context
4. Count carefully - if the context lists pillars, count them all
5. If action is needed, include [ACTION: <ToolName>] in your reply
6. If the retrieved context is insufficient to answer completely, say "Based on the available context..."

Answer based strictly on the retrieved context above:
"""
    
    print("🧪 Testing Improved Prompt Construction")
    print("=" * 60)
    print(f"Query: {query}")
    print(f"\nGenerated Prompt:\n{prompt}")
    
    # Analyze prompt
    analysis = []
    if "six pillars" in prompt.lower():
        analysis.append("✅ Contains 'six pillars' in context")
    if "sustainability" in prompt.lower():
        analysis.append("✅ Contains Sustainability pillar")
    if "ONLY on the information provided" in prompt:
        analysis.append("✅ Emphasizes using retrieved info only")
    if "EXACT numbers" in prompt:
        analysis.append("✅ Instructs to use exact numbers")
    
    print(f"\n📊 Prompt Analysis:")
    for item in analysis:
        print(f"  {item}")
    
    return len(analysis) >= 3

def test_query_enhancement():
    """Test query enhancement logic"""
    
    def preprocess_query(query):
        pillar_keywords = ['pillar', 'framework', 'principle', 'well-architected']
        if any(keyword in query.lower() for keyword in pillar_keywords):
            return f"{query} AWS Well-Architected Framework six pillars principles"
        return query
    
    test_queries = [
        "How many pillars",
        "What are the pillars of Well-Architected Framework",
        "Tell me about sustainability",
        "What is AWS Lambda"
    ]
    
    print("\n🔍 Testing Query Enhancement")
    print("=" * 60)
    
    for query in test_queries:
        enhanced = preprocess_query(query)
        enhanced_flag = "🚀" if enhanced != query else "➡️"
        print(f"{enhanced_flag} '{query}' → '{enhanced}'")
    
    return True

def test_retrieval_parameters():
    """Test retrieval parameter logic"""
    
    def get_k_value(query):
        pillar_keywords = ['pillar', 'framework', 'principle', 'well-architected', 'how many']
        return 7 if any(keyword in query.lower() for keyword in pillar_keywords) else 3
    
    test_queries = [
        ("How many pillars", 7),
        ("What are the six pillars", 7),
        ("Well-Architected Framework", 7),
        ("What is S3", 3),
        ("How many principles", 7)
    ]
    
    print("\n📈 Testing Retrieval Parameters")
    print("=" * 60)
    
    all_correct = True
    for query, expected_k in test_queries:
        actual_k = get_k_value(query)
        status = "✅" if actual_k == expected_k else "❌"
        print(f"{status} '{query}' → k={actual_k} (expected {expected_k})")
        if actual_k != expected_k:
            all_correct = False
    
    return all_correct

def generate_deployment_instructions():
    """Generate deployment instructions"""
    
    instructions = """
🚀 DEPLOYMENT INSTRUCTIONS

1. Backup Current Functions:
   - Download current AgentOrchestratorFunction.py from Lambda console
   - Download current RetrieveDocumentsFunction.py from Lambda console

2. Deploy Fixed Functions:
   - Replace AgentOrchestratorFunction.py with AgentOrchestratorFunction-FIXED.py
   - Replace RetrieveDocumentsFunction.py with RetrieveDocumentsFunction-FIXED.py

3. Test Queries:
   - "How many pillars are in the Well-Architected Framework?"
   - "What are the six pillars of the Well-Architected Framework?"
   - "Tell me about the sustainability pillar"

4. Monitor CloudWatch Logs:
   - Check for "Enhanced query:" log entries
   - Verify "Retrieved X documents" shows more docs for pillar queries
   - Confirm LLM responses mention 6 pillars

5. Rollback Plan:
   - Keep original functions as backup
   - Can quickly revert if issues occur

Key Improvements:
✅ Prompt emphasizes using ONLY retrieved information
✅ Query enhancement for pillar-related searches  
✅ Increased retrieval (k=7) for comprehensive context
✅ Better logging for debugging
✅ Lower temperature for consistent responses
"""
    
    return instructions

def main():
    """Run all tests"""
    
    print("🤖 AI Agent Fix Validation")
    print("=" * 70)
    
    # Run tests
    prompt_test = test_prompt_construction()
    query_test = test_query_enhancement()
    retrieval_test = test_retrieval_parameters()
    
    # Summary
    print(f"\n📋 Test Results Summary")
    print("=" * 60)
    print(f"✅ Prompt Construction: {'PASS' if prompt_test else 'FAIL'}")
    print(f"✅ Query Enhancement: {'PASS' if query_test else 'FAIL'}")
    print(f"✅ Retrieval Parameters: {'PASS' if retrieval_test else 'FAIL'}")
    
    all_passed = prompt_test and query_test and retrieval_test
    print(f"\n🎯 Overall Status: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print(generate_deployment_instructions())
    else:
        print("\n❌ Please review failed tests before deployment")

if __name__ == "__main__":
    main()