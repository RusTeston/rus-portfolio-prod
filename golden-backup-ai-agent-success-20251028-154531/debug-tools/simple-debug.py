#!/usr/bin/env python3
"""
Simple debug script for AI Agent - analyze embeddings without external dependencies
"""

import json

def analyze_embeddings():
    """Analyze the embeddings file to understand chunk content"""
    try:
        with open('golden-backup-20251028-051953/s3-content/projects/02-ai-agent/vectors/doc_vectors.json', 'r') as f:
            data = json.load(f)
        
        texts = data['texts']
        print(f"🤖 AI Agent Debug - Embeddings Analysis")
        print("=" * 60)
        print(f"📊 Total chunks: {len(texts)}")
        
        # Analyze pillar-related content
        pillar_chunks = []
        sustainability_chunks = []
        six_pillar_chunks = []
        
        for i, chunk in enumerate(texts):
            chunk_lower = chunk.lower()
            
            if 'pillar' in chunk_lower:
                pillar_chunks.append((i, chunk))
            
            if 'sustainability' in chunk_lower:
                sustainability_chunks.append((i, chunk))
                
            if 'six pillar' in chunk_lower or '6 pillar' in chunk_lower:
                six_pillar_chunks.append((i, chunk))
        
        print(f"\n🏛️  Chunks mentioning 'pillar': {len(pillar_chunks)}")
        print(f"🌱 Chunks mentioning 'sustainability': {len(sustainability_chunks)}")
        print(f"🎯 Chunks mentioning '6/six pillars': {len(six_pillar_chunks)}")
        
        # Show key chunks
        print(f"\n📄 Key Pillar Chunks:")
        for i, (idx, chunk) in enumerate(pillar_chunks[:5]):
            print(f"\nChunk {idx}:")
            print(f"Text: {chunk[:200]}...")
            
            # Count pillars mentioned
            if 'operational excellence' in chunk.lower():
                print("  ✅ Contains: Operational Excellence")
            if 'security' in chunk.lower():
                print("  ✅ Contains: Security")
            if 'reliability' in chunk.lower():
                print("  ✅ Contains: Reliability")
            if 'performance efficiency' in chunk.lower():
                print("  ✅ Contains: Performance Efficiency")
            if 'cost optimization' in chunk.lower():
                print("  ✅ Contains: Cost Optimization")
            if 'sustainability' in chunk.lower():
                print("  ✅ Contains: Sustainability")
        
        # Show explicit 6-pillar mentions
        if six_pillar_chunks:
            print(f"\n🎯 Explicit 6-Pillar Mentions:")
            for idx, chunk in six_pillar_chunks:
                print(f"\nChunk {idx}: {chunk}")
        
        # Search for comprehensive pillar lists
        comprehensive_chunks = []
        for i, chunk in enumerate(texts):
            pillar_count = 0
            chunk_lower = chunk.lower()
            
            if 'operational excellence' in chunk_lower: pillar_count += 1
            if 'security' in chunk_lower: pillar_count += 1
            if 'reliability' in chunk_lower: pillar_count += 1
            if 'performance efficiency' in chunk_lower: pillar_count += 1
            if 'cost optimization' in chunk_lower: pillar_count += 1
            if 'sustainability' in chunk_lower: pillar_count += 1
            
            if pillar_count >= 4:  # Chunks with multiple pillars
                comprehensive_chunks.append((i, chunk, pillar_count))
        
        print(f"\n📋 Comprehensive Chunks (4+ pillars): {len(comprehensive_chunks)}")
        for idx, chunk, count in comprehensive_chunks[:3]:
            print(f"\nChunk {idx} ({count} pillars): {chunk[:150]}...")
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: Could not find embeddings file")
        print("   Expected: golden-backup-20251028-051953/s3-content/projects/02-ai-agent/doc_vectors.json")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_current_prompt():
    """Analyze the current prompt construction"""
    print(f"\n📝 Current Prompt Analysis")
    print("=" * 60)
    
    # Simulate current prompt from AgentOrchestratorFunction.py
    sample_docs = [
        {"text": "The Well-Architected Framework has five pillars: security, reliability, performance efficiency, cost optimization, and operational excellence."},
        {"text": "AWS provides guidance on cloud architecture best practices."}
    ]
    
    query = "How many pillars"
    doc_section = "\n".join(f"- {doc['text']}" for doc in sample_docs)
    
    current_prompt = f"""
User question: {query}

Relevant documents:
{doc_section}

Available tools: NotifyHR, SummarizeDoc, CreateTask

Instructions: Provide a helpful answer. If action is needed, include [ACTION: <ToolName>] in your reply.
"""
    
    print("Current prompt structure:")
    print(current_prompt)
    
    # Identify issues
    issues = []
    if "only" not in current_prompt.lower() and "exclusively" not in current_prompt.lower():
        issues.append("❌ Doesn't emphasize using ONLY retrieved info")
    if "exact" not in current_prompt.lower():
        issues.append("❌ Doesn't instruct to use exact numbers")
    if "five pillars" in doc_section:
        issues.append("❌ Sample shows outdated 5-pillar info")
    
    print(f"\n🚨 Identified Issues:")
    for issue in issues:
        print(f"  {issue}")
    
    return len(issues)

def main():
    print("🔍 Simple AI Agent Debug Tool")
    print("=" * 50)
    
    # Analyze embeddings
    embeddings_ok = analyze_embeddings()
    
    if embeddings_ok:
        # Analyze current prompt
        issue_count = analyze_current_prompt()
        
        print(f"\n📊 Summary:")
        print(f"✅ Embeddings contain correct 6-pillar information")
        print(f"⚠️  Found {issue_count} prompt issues to fix")
        print(f"\n🎯 Next: Test the fixed functions with test-ai-agent-fixes.py")

if __name__ == "__main__":
    main()