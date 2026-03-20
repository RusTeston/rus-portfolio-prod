# AI Agent Fixes - Project 2

## Overview
This folder contains all files related to fixing the AI Agent's 6-pillar Well-Architected Framework issue.

## Folder Structure

### `/lambda-functions/`
**Production Lambda function code:**
- `AgentOrchestratorFunction-FIXED.py` - Enhanced orchestrator with strict prompts
- `RetrieveDocumentsFunction-FIXED.py` - Enhanced retrieval with k=7 search
- `AgentOrchestrator-CORS-FIX.py` - CORS handling version
- `index-*.py` - Various API format iterations (Bedrock, Claude, Titan)

### `/debug-tools/`
**Testing and debugging utilities:**
- `debug-ai-agent.py` - Comprehensive retrieval testing
- `simple-debug.py` - Embeddings analysis tool
- `test-ai-agent-fixes.py` - Fix validation tests
- `test-edge-cases.py` - Edge case testing
- `test-specific-query.py` - Query-specific tests
- `final-validation.py` - Complete validation suite
- `fix-ai-agent-prompt.py` - Prompt improvement generator
- `deploy-ai-agent-fixes.py` - Deployment automation

### `/backups/`
**Lambda function backups:**
- `AgentOrchestrator-backup-20251028-150331.zip` - Original orchestrator backup
- `RetrieveDocumentsFunction-backup-20251028-145903.zip` - Original retriever backup

### Root Files
- `AI-AGENT-FIX-SUMMARY.md` - Complete technical documentation
- `README.md` - This file

## Key Improvements Implemented
1. **Enhanced Retrieval**: Increased from k=3 to k=7 for comprehensive context
2. **Strict Prompts**: Force use of retrieved context over model knowledge
3. **Model Upgrade**: Switched to Amazon Titan Text Express for reliability
4. **CORS Handling**: Proper browser access support
5. **Query Enhancement**: Better search for pillar-related queries

## Deployment Status
✅ **Successfully deployed** - October 28, 2025
✅ **Tested and validated** - AI agent now provides accurate 6-pillar responses
✅ **Cost optimized** - ~$1/month for 500 questions with Titan Text Express

## Usage
These files serve as reference for the successful AI agent implementation and can be used for:
- Future AI agent projects
- Troubleshooting similar RAG issues
- Documentation of best practices
- Training and knowledge transfer