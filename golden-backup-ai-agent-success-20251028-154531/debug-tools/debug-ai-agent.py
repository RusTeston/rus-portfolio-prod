#!/usr/bin/env python3
"""
Debug script for AI Agent Project 2 - Well-Architected Framework issue
Tests retrieval pipeline to identify why agent returns 5 pillars instead of 6
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_embeddings():
    """Load the embeddings file to examine chunks"""
    with open('golden-backup-20251028-051953/s3-content/projects/02-ai-agent/doc_vectors.json', 'r') as f:
        data = json.load(f)
    return data['texts'], np.array(data['vectors']).astype('float32')

def create_faiss_index(vectors):
    """Create FAISS index for similarity search"""
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index

def embed_query(query):
    """Embed query using sentence transformer (approximates Titan embeddings)"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode([query])[0]

def test_retrieval(query, texts, vectors, k=3):
    """Test what chunks are retrieved for a given query"""
    print(f"\n🔍 Testing query: '{query}'")
    print("=" * 60)
    
    # Create index and search
    index = create_faiss_index(vectors)
    query_vector = np.array([embed_query(query)], dtype='float32')
    distances, indices = index.search(query_vector, k)
    
    print(f"Top {k} retrieved chunks:")
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        if idx != -1:
            chunk = texts[idx]
            print(f"\n📄 Chunk {i+1} (similarity: {1/(1+dist):.3f}):")
            print(f"Text: {chunk[:200]}...")
            
            # Check if chunk mentions pillars
            pillar_count = chunk.lower().count('pillar')
            if pillar_count > 0:
                print(f"🏛️  Contains {pillar_count} pillar mentions")
                
            # Check for sustainability
            if 'sustainability' in chunk.lower():
                print("🌱 Contains Sustainability pillar")
    
    return [texts[idx] for idx in indices[0] if idx != -1]

def analyze_prompt_construction(query, retrieved_chunks):
    """Analyze how the prompt is constructed"""
    print(f"\n📝 Prompt Construction Analysis")
    print("=" * 60)
    
    # Recreate the prompt from AgentOrchestratorFunction.py
    doc_section = "\n".join(f"- {doc}" for doc in retrieved_chunks)
    prompt = f"""
User question: {query}

Relevant documents:
{doc_section}

Available tools: NotifyHR, SummarizeDoc, CreateTask

Instructions: Provide a helpful answer. If action is needed, include [ACTION: <ToolName>] in your reply.
"""
    
    print("Generated prompt:")
    print(prompt)
    
    # Analyze prompt issues
    issues = []
    if "six" not in prompt.lower() and "6" not in prompt:
        issues.append("❌ Prompt doesn't emphasize 6 pillars")
    if "sustainability" not in prompt.lower():
        issues.append("❌ Sustainability pillar not in retrieved context")
    if len(doc_section) < 500:
        issues.append("❌ Very short context - may need more chunks")
    
    if issues:
        print("\n🚨 Potential Issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Prompt looks good - issue may be in LLM generation")

def main():
    """Main debugging function"""
    print("🤖 AI Agent Debug Tool - Well-Architected Framework Issue")
    print("=" * 70)
    
    try:
        # Load embeddings
        print("📂 Loading embeddings...")
        texts, vectors = load_embeddings()
        print(f"✅ Loaded {len(texts)} text chunks with {vectors.shape[1]}D vectors")
        
        # Test queries
        test_queries = [
            "How many pillars",
            "What are the six pillars of the Well-Architected Framework",
            "Well-Architected Framework pillars",
            "sustainability pillar"
        ]
        
        for query in test_queries:
            retrieved = test_retrieval(query, texts, vectors, k=5)
            analyze_prompt_construction(query, retrieved)
            
        # Summary analysis
        print(f"\n📊 Summary Analysis")
        print("=" * 60)
        
        # Count pillar mentions in all chunks
        pillar_chunks = [chunk for chunk in texts if 'pillar' in chunk.lower()]
        sustainability_chunks = [chunk for chunk in texts if 'sustainability' in chunk.lower()]
        
        print(f"📈 Total chunks mentioning 'pillar': {len(pillar_chunks)}")
        print(f"🌱 Total chunks mentioning 'sustainability': {len(sustainability_chunks)}")
        
        # Check for explicit 6-pillar mentions
        six_pillar_chunks = [chunk for chunk in texts if ('six pillar' in chunk.lower() or '6 pillar' in chunk.lower())]
        print(f"🎯 Chunks explicitly mentioning '6 pillars': {len(six_pillar_chunks)}")
        
        if six_pillar_chunks:
            print("\n🎯 Explicit 6-pillar mentions:")
            for chunk in six_pillar_chunks[:3]:
                print(f"  - {chunk[:100]}...")
        
    except FileNotFoundError:
        print("❌ Error: Could not find embeddings file")
        print("   Make sure you're running from the rus-portfolio-prod directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()