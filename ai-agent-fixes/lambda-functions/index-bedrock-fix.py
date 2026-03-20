import boto3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
RETRIEVER_FUNCTION = os.environ["RETRIEVER_FUNCTION"]
LLM_MODEL_ID = os.environ.get("LLM_MODEL_ID", "anthropic.claude-instant-v1")

# Clients
lambda_client = boto3.client("lambda")
bedrock = boto3.client("bedrock-runtime")

def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

def call_lambda(function_name, payload):
    logger.info(f"Invoking Lambda: {function_name}")
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )
    return json.loads(response["Payload"].read())

def get_relevant_documents(query):
    payload = {"query": query}
    response = call_lambda(RETRIEVER_FUNCTION, payload)
    documents = response.get("documents", [])
    logger.info(f"Retrieved {len(documents)} documents for query: {query}")
    return documents

def build_prompt(query, documents):
    doc_section = "\n".join(f"- {doc['text']}" for doc in documents)
    prompt = f"""
User question: {query}

CRITICAL: Base your answer ONLY on the information provided below. Do NOT use your general knowledge.

Retrieved context from AWS Well-Architected Framework documentation:
{doc_section}

Instructions: Answer using EXCLUSIVELY the retrieved context above. If the context mentions specific numbers, use those EXACT numbers.

Answer based strictly on the retrieved context:
"""
    return prompt.strip()

def call_llm(prompt):
    logger.info("Calling Bedrock LLM")
    
    # Correct format for Claude Instant v1
    body = {
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 0.1,
        "stop_sequences": ["\n\nHuman:"]
    }

    try:
        response = bedrock.invoke_model(
            modelId=LLM_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(response["body"].read())
        return result.get("completion", "").strip()
    except Exception as e:
        logger.error(f"Bedrock error: {e}")
        # Fallback response
        return "I apologize, but I'm experiencing technical difficulties. Please try again."

def lambda_handler(event, context):
    try:
        # Handle CORS preflight
        if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": get_cors_headers(),
                "body": ""
            }

        logger.info(f"Processing request")

        # Parse input from Lambda Function URL format
        user_input = ""
        
        if 'body' in event:
            try:
                body_data = json.loads(event['body'])
                user_input = body_data.get('query', '')
            except:
                pass
        
        if not user_input:
            user_input = event.get("query") or ""

        if not user_input:
            return {
                "statusCode": 400,
                "headers": get_cors_headers(),
                "body": json.dumps({"error": "Missing query input"})
            }

        logger.info(f"Query: {user_input}")

        # Step 1: Retrieve documents
        docs = get_relevant_documents(user_input)

        # Step 2: Build prompt
        prompt = build_prompt(user_input, docs)

        # Step 3: Call LLM
        llm_response = call_llm(prompt)

        # Step 4: Return response
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({
                "answer": llm_response
            })
        }

    except Exception as e:
        logger.exception("Agent orchestrator error")
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": "Internal server error"})
        }