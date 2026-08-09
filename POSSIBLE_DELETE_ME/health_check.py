#!/usr/bin/env python3
"""
Portfolio Health Check
Runs end-to-end tests across all three sites and AI services.
Usage: python3 health_check.py
"""

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"

results = []

def check(name, passed, detail=""):
    status = PASS if passed else FAIL
    results.append((name, passed, detail))
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))

def http_get(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)

def http_post(url, payload, timeout=15):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
            "User-Agent": "HealthCheck/1.0"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}

def aws(cmd):
    try:
        r = subprocess.run(["aws"] + cmd, capture_output=True, text=True, timeout=30)
        return r.returncode == 0, r.stdout.strip()
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
print("\n" + "="*55)
print("  PORTFOLIO HEALTH CHECK")
print("="*55)

# ─── SITE AVAILABILITY ───────────────────────
print("\n[ Site Availability ]")
for label, url in [
    ("rus-teston.com homepage",     "https://rus-teston.com/"),
    ("rus-teston.com resume page",  "https://rus-teston.com/resume.html"),
    ("rus-teston.com resume PDF",   "https://rus-teston.com/assets/resume/William_Teston_General.pdf"),
    ("rus-teston.com welcome video","https://rus-teston.com/assets/video/Rus_Webpage_Welcome.mp4"),
    ("ai.rus-teston.com homepage",  "https://ai.rus-teston.com/"),
    ("nebius.rus-teston.com splash","https://nebius.rus-teston.com/"),
    ("nebius.rus-teston.com projects","https://nebius.rus-teston.com/projects.html"),
    ("Sales Quiz app",              "https://d2lgw3pldlv4g9.cloudfront.net/"),
]:
    code, _ = http_get(url)
    check(label, code == 200, f"HTTP {code}")

# ─── VISITOR TRACKER ─────────────────────────
print("\n[ Visitor Tracker ]")
code, body = http_get("https://h02rwkd6hl.execute-api.us-east-1.amazonaws.com/prod/track")
try:
    d = json.loads(body)
    check("Visitor tracker API", code == 200, f"total visits: {d.get('total_visits','?')}")
except Exception:
    check("Visitor tracker API", False, f"HTTP {code}")

# ─── BEDROCK MODEL AVAILABILITY ──────────────
print("\n[ Bedrock Model Availability ]")
# Nova Lite - verify via direct invoke (availability API not supported for Amazon models)
try:
    import boto3
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    r = client.invoke_model(
        modelId='us.amazon.nova-lite-v1:0',
        body=json.dumps({'messages':[{'role':'user','content':[{'text':'Say OK'}]}],'inferenceConfig':{'maxTokens':5}}),
        contentType='application/json', accept='application/json'
    )
    check('Bedrock Nova Lite', True, 'AVAILABLE')
except Exception as e:
    check('Bedrock Nova Lite', False, str(e)[:60])

for model_id, label in [
    ("us.anthropic.claude-sonnet-4-6",              "Claude Sonnet 4.6"),
    ("us.anthropic.claude-sonnet-4-5-20250929-v1:0","Claude Sonnet 4.5"),
]:
    ok, out = aws(["bedrock", "get-foundation-model-availability",
                   "--model-id", model_id, "--region", "us-east-1",
                   "--output", "json"])
    try:
        d = json.loads(out)
        authorized = d.get("authorizationStatus") == "AUTHORIZED"
        check(f"Bedrock {label}", ok and authorized, d.get("authorizationStatus", out[:40]))
    except Exception:
        check(f"Bedrock {label}", False, out[:60])

# ─── AI CHATBOT (Project 1) ──────────────────
print("\n[ Project 1 - AI Chatbot ]")
code, body = http_post(
    "https://ri802yjmt0.execute-api.us-east-1.amazonaws.com/prod/chat",
    {"message": "What is AWS S3 in one sentence?"}
)
r = body.get("response", body.get("message", ""))
check("AI Chatbot (Nova Lite)", bool(r) and "error" not in str(r).lower(), str(r)[:60] + "..." if len(str(r)) > 60 else str(r))

# ─── LANGUAGE TRANSLATOR (Project 3) ─────────
print("\n[ Project 3 - Language Translator ]")
code, body = http_post(
    "https://3usd2qizpvp57tsk6b4qkifnym0lnkdi.lambda-url.us-east-1.on.aws/",
    {"text": "Hello", "sourceLanguage": "en", "targetLanguage": "es"}
)
inner = json.loads(body.get("body", "{}")) if isinstance(body.get("body"), str) else body
t = inner.get("translatedText", inner.get("translated_text", ""))
check("Language Translator (AWS Translate)", bool(t) and "error" not in str(inner).lower(), t)

# ─── DOCUMENT INTELLIGENCE (Project 4) ───────
print("\n[ Project 4 - Document Intelligence ]")
try:
    data = b"Invoice #1234 Total: $500"
    req = urllib.request.Request(
        "https://o73axp5a7fzg2nti6rhavce3qa0rxlcj.lambda-url.us-east-1.on.aws/upload?filename=test.txt",
        data=data, headers={"Content-Type": "application/octet-stream"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
        inner = json.loads(resp.get("body", "{}")) if isinstance(resp.get("body"), str) else resp
        check("Doc Intelligence upload", "error" not in str(inner).lower(), inner.get("message", str(inner)[:60]))
except Exception as e:
    check("Doc Intelligence upload", False, str(e))

# ─── TEXT-TO-SPEECH (Project 5) ──────────────
print("\n[ Project 5 - Text-to-Speech ]")
try:
    data = b"Hello this is a test."
    req = urllib.request.Request(
        "https://re7denuxpksnsoet2qbklz7np40bbfhn.lambda-url.us-east-1.on.aws/upload?filename=hc_test.txt&voiceEngine=neural&voiceId=Joanna",
        data=data, headers={"Content-Type": "application/octet-stream"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
        inner = json.loads(resp.get("body", "{}")) if isinstance(resp.get("body"), str) else resp
        uploaded = "error" not in str(inner).lower()
    check("TTS upload", uploaded, inner.get("message", ""))
    if uploaded:
        time.sleep(10)
        code2, body2 = http_get(
            "https://re7denuxpksnsoet2qbklz7np40bbfhn.lambda-url.us-east-1.on.aws/result?filename=hc_test.txt"
        )
        try:
            r2 = json.loads(body2)
            inner2 = json.loads(r2.get("body", "{}")) if isinstance(r2.get("body"), str) else r2
            sc = r2.get("statusCode", code2)
            check("TTS Polly processing", sc == 200, f"voice={inner2.get('voice_id','?')} chars={inner2.get('text_length','?')}")
        except Exception as e:
            check("TTS Polly processing", False, str(e))
except Exception as e:
    check("TTS upload", False, str(e))

# ─── COST OPTIMIZER (Project 6) ──────────────
print("\n[ Project 6 - Cost Optimizer ]")
code, body = http_post("https://lrgznk1b2g.execute-api.us-east-1.amazonaws.com/Prod/scan", {})
inner = json.loads(body.get("body", "{}")) if isinstance(body.get("body"), str) else body
check("Cost Optimizer (Nova Lite)", "error" not in str(inner).lower() and code in [200, 201], f"status={inner.get('status', code)}")

# ─── ARCHITECTURE REVIEWER (Project 7) ───────
print("\n[ Project 7 - Architecture Reviewer ]")
code, body = http_post(
    "https://09gdl2y743.execute-api.us-east-1.amazonaws.com/Prod/analyze",
    {"template": "AWSTemplateFormatVersion: 2010-09-09\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket"}
)
job_id = body.get("jobId", "")
check("Architecture Reviewer submit", bool(job_id), f"jobId={job_id[:16]}..." if job_id else "no jobId")
if job_id:
    time.sleep(8)
    code2, body2 = http_get(f"https://09gdl2y743.execute-api.us-east-1.amazonaws.com/Prod/results/{job_id}")
    try:
        r2 = json.loads(body2)
        check("Architecture Reviewer result", r2.get("status") == "COMPLETE", f"status={r2.get('status','?')}")
    except Exception as e:
        check("Architecture Reviewer result", False, str(e))

# ─── LOG ANALYZER (Project 8) ────────────────
print("\n[ Project 8 - Log Analyzer ]")
try:
    data = b"ERROR: Connection timeout\nWARN: High memory usage"
    req = urllib.request.Request(
        "https://gjktxu3tgjrvniffzqon2uqhvm0budfq.lambda-url.us-east-1.on.aws/upload?filename=hc_test.log",
        data=data, headers={"Content-Type": "application/octet-stream"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
        inner = json.loads(resp.get("body", "{}")) if isinstance(resp.get("body"), str) else resp
        check("Log Analyzer upload", "error" not in str(inner).lower(), inner.get("message", str(inner)[:60]))
except Exception as e:
    check("Log Analyzer upload", False, str(e))

# ─── FAILOVER ORCHESTRATOR (Project 9) ───────
print("\n[ Project 9 - Failover Orchestrator ]")
code, body = http_get("https://d6dnpz3c39.execute-api.us-east-1.amazonaws.com/Prod/status")
try:
    d = json.loads(body) if body.strip().startswith('{') else {"raw": body[:60]}
    check("Failover Orchestrator status", code == 200, f"HTTP {code}")
except Exception:
    check("Failover Orchestrator status", code == 200, f"HTTP {code}")

# ─── PROMPT BUILDER (Project 10) ─────────────
print("\n[ Project 10 - Prompt Builder ]")
code, body = http_post(
    "https://n7taftgspogdij7l4g2ercpnsi0srofk.lambda-url.us-east-1.on.aws/",
    {"prompt": "Explain AWS S3", "role": "assistant", "task": "explain"}
)
inner = json.loads(body.get("body", "{}")) if isinstance(body.get("body"), str) else body
r = inner.get("enhanced_prompt", inner.get("prompt", inner.get("response", "")))
check("Prompt Builder (Nova Lite)", bool(r) and "error" not in str(inner).lower(), str(r)[:60] + "..." if len(str(r)) > 60 else str(r))

# ─── RESUME RADAR (rus-teston.com Project 5) ─
print("\n[ Resume Radar (rus-teston.com) ]")
code, body = http_post(
    "https://o7ncz2qninqxstd4dbz6yvvdkq0rrebi.lambda-url.us-east-1.on.aws/",
    {"resume": "AWS Solutions Architect 8 years experience.", "job_description": "Senior Cloud Architect AWS required."}
)
inner = json.loads(body.get("body", "{}")) if isinstance(body.get("body"), str) else body
score = inner.get("match_score", inner.get("score", inner.get("matchScore", None)))
check("Resume Radar (Nova Lite)", score is not None and "error" not in str(inner).lower(), f"match score: {score}")

# ─── SALES QUIZ API (Project 17) ─────────────
print("\n[ Project 17 - Sales Quiz ]")
code, body = http_get("https://5p2xkz9is7.execute-api.us-east-1.amazonaws.com/prod/questions?role=AE&difficulty=B&format=MC")
try:
    d = json.loads(body)
    check("Sales Quiz API", code == 200 and isinstance(d, list), f"{len(d)} questions returned")
except Exception:
    check("Sales Quiz API", False, f"HTTP {code}")

# ─── TOKEN FACTORY PROXY (Nebius Project 10) ─
print("\n[ Nebius Token Factory (DeepSeek V3.2) ]")
code, body = http_post(
    "https://og7jfo5coewn245brfxmygjzaq0pebxk.lambda-url.us-east-1.on.aws/",
    {"question": "What is a GPU in one sentence?"}
)
inner = json.loads(body.get("body", "{}")) if isinstance(body.get("body"), str) else body
answer = inner.get("answer", "")
check("Token Factory proxy", bool(answer) and "error" not in str(inner).lower(), str(answer)[:60] + "..." if len(str(answer)) > 60 else str(answer))

# ─── SUMMARY ─────────────────────────────────
total = len(results)
passed = sum(1 for _, p, _ in results if p)
failed = total - passed

print("\n" + "="*55)
print(f"  RESULTS: {passed}/{total} passed", end="")
if failed:
    print(f"  |  {failed} FAILED")
else:
    print("  - ALL SYSTEMS GO")
print("="*55)

if failed:
    print("\nFailed checks:")
    for name, p, detail in results:
        if not p:
            print(f"  - {name}: {detail}")

print()
sys.exit(0 if failed == 0 else 1)
