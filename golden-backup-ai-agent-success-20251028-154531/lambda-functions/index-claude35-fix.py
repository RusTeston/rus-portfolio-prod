import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
RETRIEVER_FUNCTION = os.environ["RETRIEVER_FUNCTION"]
LLM_MODEL_ID = os.environ.get("LLM_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")

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
    return documents

def build_prompt(query, documents):
    doc_section = "\n".join(f"- {doc['text']}" for doc in documents)
    return f"""User question: {query}

CRITICAL: Base your answer ONLY on the information provided below.

Retrieved context:
{doc_section}

Answer using EXCLUSIVELY the retrieved context above:"""

def call_llm(prompt):
    try:
        # Claude 3.5 API format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId=LLM_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
        
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        return f"Error calling AI model: {str(e)}"

def lambda_handler(event, context):
    try:
        # Handle CORS preflight
        if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": get_cors_headers(),
                "body": ""
            }

        # Parse input
        user_input = ""
        if 'body' in event:
            try:
                body_data = json.loads(event['body'])
                user_input = body_data.get('query', '')
            except:
                pass
        
        if not user_input:
            return {
                "statusCode": 400,
                "headers": get_cors_headers(),
                "body": json.dumps({"error": "Missing query"})
            }

        logger.info(f"Processing: {user_input}")

        # Get documents and generate response
        docs = get_relevant_documents(user_input)
        prompt = build_prompt(user_input, docs)
        response = call_llm(prompt)

        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({"answer": response})
        }

    except Exception as e:
        logger.exception("Handler error")
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": f"Server error: {str(e)}"})
        }