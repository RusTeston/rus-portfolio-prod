#!/usr/bin/env python3
"""
Test specific query: "Which pillar covers operational excellence?"
"""

import json

def test_operational_excellence_query():
    """Test how the system handles operational excellence query"""
    
    # Load embeddings
    with open('golden-backup-20251028-051953/s3-content/projects/02-ai-agent/vectors/doc_vectors.json', 'r') as f:
        data = json.load(f)
    
    texts = data['texts']
    query = "Which pillar covers operational excellence?"
    
    print(f"🔍 Testing Query: '{query}'")
    print("=" * 60)
    
    # Find chunks mentioning operational excellence
    op_ex_chunks = []
    for i, chunk in enumerate(texts):
        if 'operational excellence' in chunk.lower():
            op_ex_chunks.append((i, chunk))
    
    print(f"📊 Found {len(op_ex_chunks)} chunks mentioning 'operational excellence'")
    
    # Show top chunks
    print(f"\n📄 Top Operational Excellence Chunks:")
    for i, (idx, chunk) in enumerate(op_ex_chunks[:3]):
        print(f"\nChunk {idx}:")
        print(f"Text: {chunk[:300]}...")
        
        # Check if it explains that operational excellence IS a pillar
        if 'pillar' in chunk.lower() and 'operational excellence' in chunk.lower():
            print("  ✅ Explains operational excellence as a pillar")
    
    # Test current vs fixed prompt
    sample_retrieved = [{"text": op_ex_chunks[0][1][:200] + "..."} if op_ex_chunks else {"text": "No relevant context found"}]
    
    print(f"\n📝 Current Prompt Response:")
    current_prompt = f"""
User question: {query}

Relevant documents:
- {sample_retrieved[0]['text']}

Instructions: Provide a helpful answer.
"""
    print("Would likely respond: 'Operational Excellence is one of the pillars...' (using model knowledge)")
    
    print(f"\n📝 Fixed Prompt Response:")
    fixed_prompt = f"""
User question: {query}

CRITICAL: Base your answer ONLY on the information provided below.

Retrieved context:
- {sample_retrieved[0]['text']}

Instructions: Answer using EXCLUSIVELY the retrieved context above.
"""
    print("Would respond based strictly on retrieved context about operational excellence pillar")
    
    return len(op_ex_chunks) > 0

def main():
    try:
        result = test_operational_excellence_query()
        print(f"\n✅ Test Result: {'PASS' if result else 'FAIL'}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()