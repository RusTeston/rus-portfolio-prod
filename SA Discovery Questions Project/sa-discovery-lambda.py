import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

HEADERS = {"Content-Type": "application/json"}

def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": HEADERS, "body": ""}

    try:
        body = json.loads(event.get("body", "{}"))
        notes = body.get("notes", "").strip()
        already_asked = body.get("already_asked", [])

        if not notes:
            return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "notes required"})}

        already_block = ""
        if already_asked:
            already_block = f"\nThese questions have already been covered, do not repeat them:\n- " + "\n- ".join(already_asked) + "\n"

        prompt = f"""You are a senior AWS Solutions Architect helping a colleague prepare discovery questions during a live customer meeting about migrating on-premises infrastructure to AWS.

Here are the customer's raw meeting notes so far:
\"\"\"
{notes}
\"\"\"{already_block}
Generate the 6-8 MOST IMPORTANT follow-up discovery questions that are specific to what's actually mentioned in these notes (not generic boilerplate). Favor questions that materially change the AWS architecture or migration strategy recommendation (e.g. choice between rehost/replatform/refactor, managed vs self-managed services, licensing, compliance, sizing, dependencies, timeline risk).

Respond with ONLY a raw JSON array, no markdown fences, no prose. Each element must have exactly these keys:
"category": a short 2-4 word label
"question": the question to ask the customer, phrased naturally
"why": one short sentence on why this answer changes the AWS recommendation"""

        response = bedrock.converse(
            modelId="us.amazon.nova-lite-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1200, "temperature": 0.4}
        )

        raw = response["output"]["message"]["content"][0]["text"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)

        return {"statusCode": 200, "headers": HEADERS, "body": json.dumps(parsed)}

    except Exception as e:
        return {"statusCode": 500, "headers": HEADERS, "body": json.dumps({"error": str(e)})}
