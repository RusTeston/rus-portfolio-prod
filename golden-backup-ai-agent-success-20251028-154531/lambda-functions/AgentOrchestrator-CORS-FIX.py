import boto3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
RETRIEVER_FUNCTION = os.environ["RETRIEVER_FUNCTION"]
TOOL_FUNCTIONS = {
    "NotifyHR": os.environ.get("NOTIFY_HR_FUNCTION"),
    "SummarizeDoc": os.environ.get("SUMMARIZE_DOC_FUNCTION"),
    "CreateTask": os.environ.get("CREATE_TASK_FUNCTION"),
}
LLM_MODEL_ID = os.environ.get("LLM_MODEL_ID", "anthropic.claude-instant-v1")

# Clients
lambda_client = boto3.client("lambda")
bedrock = boto3.client("bedrock-runtime")

def get_cors_headers():
    """Return CORS headers for browser requests"""
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
    return prompt.strip()

def call_llm(prompt):
    logger.info("Calling Bedrock LLM")
    body = {
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 500,
        "temperature": 0.1,
        "stop_sequences": ["\n\nHuman:"]
    }

    response = bedrock.invoke_model(
        modelId=LLM_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response["body"].read())
    return result.get("completion", "").strip()

def parse_actions(response):
    actions = []
    for tool in TOOL_FUNCTIONS:
        tag = f"[ACTION: {tool}]"
        if tag in response:
            actions.append(tool)
    return actions

def lambda_handler(event, context):
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": get_cors_headers(),
                "body": ""
            }

        logger.info(f"Incoming event: {json.dumps(event)}")

        user_input = event.get("inputTranscript") or \
                     event.get("UserInput") or \
                     event.get("query") or \
                     event.get("text") or ""

        if not user_input:
            return {
                "statusCode": 400,
                "headers": get_cors_headers(),
                "body": json.dumps({"error": "Missing query input"})
            }

        # Step 1: Retrieve documents
        docs = get_relevant_documents(user_input)

        # Step 2: Build prompt
        prompt = build_prompt(user_input, docs)
        logger.info(f"Generated prompt: {prompt[:200]}...")

        # Step 3: Call LLM
        llm_response = call_llm(prompt)
        logger.info(f"LLM response: {llm_response}")

        # Step 4: Parse and execute tool actions
        actions = parse_actions(llm_response)
        triggered = []

        for action in actions:
            function_name = TOOL_FUNCTIONS.get(action)
            if function_name:
                result = call_lambda(function_name, {
                    "userId": "123",
                    "task": f"{action} triggered by query: {user_input}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                triggered.append({action: result})

        # Step 5: Return final response with CORS headers
        return {
            "statusCode": 200,
            "headers": get_cors_headers(),
            "body": json.dumps({
                "answer": llm_response,
                "tools_triggered": triggered,
                "debug_info": {
                    "documents_retrieved": len(docs),
                    "query": user_input
                }
            })
        }

    except Exception as e:
        logger.exception("Agent orchestrator error")
        return {
            "statusCode": 500,
            "headers": get_cors_headers(),
            "body": json.dumps({"error": str(e)})
        }