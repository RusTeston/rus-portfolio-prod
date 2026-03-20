import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RETRIEVER_FUNCTION = os.environ["RETRIEVER_FUNCTION"]
LLM_MODEL_ID = os.environ.get("LLM_MODEL_ID", "amazon.titan-text-express-v1")

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

def call_llm(prompt):
    try:
        # Titan API format
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 300,
                "temperature": 0.1,
                "stopSequences": []
            }
        }

        response = bedrock.invoke_model(
            modelId=LLM_MODEL_ID,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        result = json.loads(response["body"].read())
        return result["results"][0]["outputText"].strip()
        
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        return f"Error: {str(e)}"

def lambda_handler(event, context):
    try:
        if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": get_cors_headers(),
                "body": ""
            }

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

        docs = get_relevant_documents(user_input)
        doc_section = "\n".join(f"- {doc['text']}" for doc in docs)
        
        prompt = f"""Question: {user_input}

Context from AWS Well-Architected Framework:
{doc_section}

Answer using ONLY the context above:"""

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