#!/usr/bin/env python3
"""
Fix AI Agent prompt to emphasize using retrieved information over model knowledge
"""

def generate_improved_prompt():
    """Generate improved prompt for AgentOrchestratorFunction.py"""
    
    improved_prompt = '''def build_prompt(query, documents):
    doc_section = "\\n".join(f"- {doc['text']}" for doc in documents)
    prompt = f"""
User question: {query}

IMPORTANT: Base your answer ONLY on the information provided below. Do NOT use your general knowledge.

Retrieved context from official AWS documentation:
{doc_section}

Available tools: NotifyHR, SummarizeDoc, CreateTask

Instructions: 
1. Answer using ONLY the information from the retrieved context above
2. If the context mentions specific numbers (like "six pillars"), use those exact numbers
3. Include all pillars/components mentioned in the retrieved context
4. If action is needed, include [ACTION: <ToolName>] in your reply
5. If the retrieved context is insufficient, say "I need more specific information"

Answer based strictly on the retrieved context:
"""
    return prompt.strip()'''
    
    return improved_prompt

def generate_retrieval_improvements():
    """Generate improvements for RetrieveDocumentsFunction.py"""
    
    improvements = '''# Suggested improvements for RetrieveDocumentsFunction.py:

1. Increase k value for pillar-related queries:
   
   def lambda_handler(event, context):
       query = event.get("query")
       
       # Increase retrieval for pillar queries
       k = 5 if any(word in query.lower() for word in ['pillar', 'framework', 'principle']) else 3
       
       D, I = faiss_index.search(query_vector, k)

2. Add query preprocessing:
   
   def preprocess_query(query):
       """Expand pillar-related queries for better retrieval"""
       pillar_keywords = ['pillar', 'framework', 'principle']
       if any(keyword in query.lower() for keyword in pillar_keywords):
           return f"{query} AWS Well-Architected Framework pillars principles"
       return query

3. Add logging for debugging:
   
   logger.info(f"Query: {query}")
   logger.info(f"Retrieved {len(results)} documents")
   for i, doc in enumerate(results):
       logger.info(f"Doc {i}: {doc['text'][:100]}...")'''
   
   return improvements

def main():
    print("🔧 AI Agent Prompt Improvement Generator")
    print("=" * 50)
    
    print("\n📝 Improved prompt function:")
    print(generate_improved_prompt())
    
    print("\n🔍 Retrieval improvements:")
    print(generate_retrieval_improvements())
    
    print("\n✅ Next steps:")
    print("1. Run debug-ai-agent.py to see current retrieval results")
    print("2. Update AgentOrchestratorFunction.py with improved prompt")
    print("3. Update RetrieveDocumentsFunction.py with retrieval improvements")
    print("4. Test with queries: 'How many pillars' and 'What are the six pillars'")

if __name__ == "__main__":
    main()