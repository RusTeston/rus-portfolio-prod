import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "us.amazon.nova-pro-v1:0"
MAX_TOKENS = 8000


def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return cors_response(200, "")

    try:
        # Parse request body
        body = json.loads(event.get("body") or "{}")
        diagram_type = body.get("type", "aws")
        description  = body.get("description", "")
        if isinstance(description, str):
            description = description.strip()

        if diagram_type != "migration" and not description:
            return cors_response(400, json.dumps({"error": "description is required"}))
        if diagram_type == "migration" and not (description.get("onprem") and description.get("aws")):
            return cors_response(400, json.dumps({"error": "both onprem and aws descriptions required"}))

        if diagram_type not in ("aws", "onprem", "migration"):
            return cors_response(400, json.dumps({"error": "type must be aws, onprem, or migration"}))

        # Build prompts
        if diagram_type == "migration":
            system_prompt = build_migration_prompt()
            user_message  = f"On-premises environment:\n{description.get('onprem','')}\
\n\nProposed AWS environment:\n{description.get('aws','')}"
        elif diagram_type == "aws":
            system_prompt = build_aws_prompt()
            user_message  = f"Generate a detailed AWS architecture SVG diagram for the following environment:\n\n{description}"
        else:
            system_prompt = build_onprem_prompt()
            user_message  = f"Generate a detailed on-premises infrastructure SVG diagram for the following environment:\n\n{description}"

        # Call Bedrock
        logger.info(f"Invoking Bedrock model={MODEL_ID} type={diagram_type}")
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": system_prompt + "\n\n" + user_message}
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 8000
                }
            })
        )

        result = json.loads(response["body"].read())
        svg_raw = result.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")

        # Migration returns HTML analysis, not SVG
        if diagram_type == "migration":
            if not svg_raw:
                return cors_response(500, json.dumps({"error": "No analysis returned. Please try again."}))
            logger.info("Migration analysis generated successfully")
            return cors_response(200, json.dumps({"html": svg_raw}))

        svg = extract_svg(svg_raw)

        if not svg:
            logger.error("No SVG found in Bedrock response")
            return cors_response(500, json.dumps({"error": "No SVG in response. Please try again."}))

        logger.info("SVG extracted successfully")
        return cors_response(200, json.dumps({"svg": svg}))

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return cors_response(500, json.dumps({"error": str(e)}))


def extract_svg(text):
    """Extract SVG content from model response."""
    # Strip XML declaration and markdown fences
    text = text.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>", "").strip()
    for fence in ["```svg", "```xml", "```html", "```"]:
        if text.startswith(fence):
            text = text[len(fence):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    start = text.find("<svg")
    end   = text.rfind("</svg>")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 6]
    return None


def cors_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": body
    }


def build_aws_prompt():
    return """You are an expert AWS Solutions Architect and infrastructure diagramming specialist. Generate a highly detailed, professional SVG AWS architecture diagram.

ABSOLUTE OUTPUT RULE: The ENTIRE response must be valid SVG code and NOTHING ELSE.
- First character of your response: <
- Last character of your response: >
- Zero prose, zero explanation, zero markdown, zero code fences

SVG CANVAS:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950">

ALWAYS INCLUDE THESE SVG DEFS:
<defs>
  <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#4B5563"/></marker>
  <marker id="arr-org" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#FF9900"/></marker>
</defs>

LAYOUT (y positions):
- y=0-50: Title bar (fill="#232F3E", white text, 18px bold, show region label)
- y=55-130: External tier — Users/Internet icon, CloudFront, Route 53, WAF (OUTSIDE VPC)
- y=135-165: Internet Gateway bar
- y=165-920: AWS Region box (stroke="#232F3E" stroke-dasharray="6,3" fill="#FAFBFC")
  INSIDE REGION:
  y=175-910: VPC box (stroke="#FF9900" stroke-width="2" fill="#FFFEF7" rx="6")
    INSIDE VPC — show Availability Zones side by side:
    Each AZ: stroke="#232F3E" stroke-dasharray="4,3" fill="#F8F9FA" rx="4"

    SUBNET COLOR CODE:
    - Public subnet:   stroke="#2E7D32" stroke-width="1.5" fill="#F1F8E9"
    - Private subnet:  stroke="#1565C0" stroke-width="1.5" fill="#E8F0FE"
    - Database subnet: stroke="#6A1B9A" stroke-width="1.5" fill="#F3E5F5"

    Label each subnet: "Public Subnet" or "Private Subnet" + CIDR (e.g. 10.0.1.0/24)

SERVICE BOX FORMAT (inside subnets):
<rect width="150" height="60" fill="white" stroke="#E5E7EB" rx="5"/>
<rect width="150" height="10" fill="{SERVICE_COLOR}" rx="5"/>
<rect width="150" height="5" y="5" fill="{SERVICE_COLOR}"/>
<text x="8" y="26" font-size="11" font-weight="bold">{SERVICE_NAME}</text>
<text x="8" y="40" font-size="9" fill="#6B7280">{DESCRIPTION}</text>

SERVICE COLOR STRIPS:
- IGW / NAT GW:    #FF9900
- ALB / NLB:       #1565C0
- EC2 / ECS / EKS: #FF9900
- Lambda:          #FF9900
- RDS / Aurora:    #6A1B9A
- ElastiCache:     #C62828
- S3:              #2E7D32
- CloudFront:      #8B5CF6
- WAF:             #DC2626
- Route 53:        #8B5CF6
- CloudWatch:      #1565C0
- SQS / SNS:       #E65100
- Bedrock:         #01A88D

CONNECTIVITY:
- Users to CloudFront/ALB: stroke="#FF9900" stroke-width="2" marker-end="url(#arr-org)"
- Inter-service arrows: stroke="#4B5563" stroke-width="1.5" marker-end="url(#arr)"
- Label every arrow: font-size="9" fill="#6B7280" e.g. "HTTPS/443", "MySQL/3306"
- NAT GW outbound: arrow from private subnet through NAT to IGW labeled "Outbound only"

ADDITIONAL ELEMENTS:
- VPC CIDR label inside VPC top-left: font-size="10" fill="#92400E"
- AZ labels (us-east-1a, us-east-1b): inside AZ box top-center, font-size="10" bold
- CloudWatch: small box outside VPC lower-right
- S3 bucket: outside VPC right side if applicable

LEGEND (bottom-right ~240x160):
- White box, border, title "LEGEND"
- Rows: colored rectangle + label for Public Subnet, Private Subnet, DB Subnet, VPC, AZ, Arrow

Draw a rich, accurate, well-spaced AWS diagram using the FULL 1400x950 canvas. Show all connections with labeled arrows."""


def build_onprem_prompt():
    return """You are an expert data center infrastructure diagramming specialist. Generate a highly detailed, professional SVG diagram for on-premises infrastructure.

ABSOLUTE OUTPUT RULE: The ENTIRE response must be valid SVG code and NOTHING ELSE.
- First character of your response: <
- Last character of your response: >
- Zero prose, zero explanation, zero markdown, zero code fences

SVG CANVAS:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 950" width="1400" height="950">

ALWAYS INCLUDE THESE SVG DEFS:
<defs>
  <marker id="arr" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#4B5563"/></marker>
  <marker id="arr-red" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#DC2626"/></marker>
  <marker id="arr-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0,10 3.5,0 7" fill="#2563EB"/></marker>
</defs>

LAYOUT (y positions):
- y=0-50: Title bar (fill="#0A1628", white text, 18px bold)
- y=55-145: Internet / WAN zone
- y=150-310: DMZ zone (if present)
- y=315-690: Core internal network zones (tiers)
- y=695-850: Storage / backup / management zones
- y=855-950: Legend box (bottom-right)

COMPONENT COLOR RULES:
- Background: <rect width="1400" height="950" fill="#F8FAFC"/>
- Internet/WAN zone: fill="#F1F5F9" stroke="#94A3B8" stroke-dasharray="8,4"
- DMZ zone: fill="#FFF7ED" stroke="#F97316" stroke-dasharray="6,3" stroke-width="2"
- Internal zone: fill="#EFF6FF" stroke="#3B82F6" stroke-dasharray="6,3" stroke-width="2"
- Server tier zone (App): fill="#F0FDF4" stroke="#22C55E" stroke-dasharray="6,3"
- Server tier zone (DB): fill="#FAF5FF" stroke="#A855F7" stroke-dasharray="6,3"
- Management zone: fill="#FEF9C3" stroke="#EAB308" stroke-dasharray="6,3"
- Server box: fill="#1E3A8A" rx="5" (white text, 11px)
- Firewall box: fill="#B91C1C" rx="4" (white text, bold)
- Switch box: fill="#1F2937" rx="3" (white text)
- Load balancer box: fill="#B45309" rx="4" (white text)
- Storage box: fill="#6D28D9" rx="4" (white text)
- Monitoring box: fill="#065F46" rx="4" (white text)

CONNECTIVITY RULES:
- Use <line> or <path> with stroke="#4B5563" stroke-width="1.5" marker-end="url(#arr)"
- For firewall connections: stroke="#DC2626" marker-end="url(#arr-red)"
- Add small <text> labels on arrows (font-size="9" fill="#6B7280")

LEGEND (bottom-right ~200x140px):
- White box with border, title "LEGEND"
- Color swatches + labels for Firewall, Server, Switch, LB, Storage, Arrow

Draw a rich, detailed, spatially accurate diagram. Spread components across the full 1400px width. Use all vertical space."""


def build_migration_prompt():
    return """You are an expert AWS Solutions Architect specializing in cloud migration strategy. Analyze the provided on-premises environment and proposed AWS architecture, then generate a professional migration analysis report in clean HTML.

OUTPUT RULE: Return only valid HTML fragments (no <!DOCTYPE>, no <html>, no <head>, no <body> tags). Just the inner content that will be injected into a styled container.

Generate the following four sections using these exact HTML structures:

1. SUMMARY BAR — key metrics as a flex row:
<div class="summary-bar">
  <div class="sb-item"><div class="sb-label">Components Mapped</div><div class="sb-value blue">X of Y</div></div>
  <div class="sb-item"><div class="sb-label">Migration Pattern</div><div class="sb-value">Replatform / Rehost / Refactor</div></div>
  <div class="sb-item"><div class="sb-label">Estimated Cost Savings</div><div class="sb-value green">XX-XX%</div></div>
  <div class="sb-item"><div class="sb-label">Target Availability</div><div class="sb-value aws">99.XX%</div></div>
  <div class="sb-item"><div class="sb-label">DR Strategy</div><div class="sb-value">brief description</div></div>
</div>

2. COMPONENT MAPPING TABLE — map every on-prem component to its AWS equivalent:
<div class="section-heading"><div class="sh-dot" style="background:#2563EB"></div>Component Mapping — On-Premises to AWS</div>
<table class="mapping-table">
  <thead><tr><th>On-Premises</th><th></th><th>AWS Equivalent</th><th>Why This Service</th></tr></thead>
  <tbody>
    <tr>
      <td><span class="onprem-tag">Component Name</span></td>
      <td class="arrow-cell">→</td>
      <td><span class="aws-tag">AWS Service Name</span></td>
      <td class="reason-cell">Brief reason why this AWS service is the right replacement.</td>
    </tr>
  </tbody>
</table>

3. KEY BENEFITS — exactly 3 cards:
<div class="section-heading"><div class="sh-dot" style="background:#059669"></div>Key Business Benefits</div>
<div class="benefits-grid">
  <div class="benefit-card"><div class="bc-icon">💰</div><div class="bc-title">Cost Optimization</div><div class="bc-desc">specific cost benefit</div></div>
  <div class="benefit-card"><div class="bc-icon">⚡</div><div class="bc-title">Scalability & Resilience</div><div class="bc-desc">specific resilience benefit</div></div>
  <div class="benefit-card"><div class="bc-icon">🔧</div><div class="bc-title">Operational Efficiency</div><div class="bc-desc">specific operational benefit</div></div>
</div>

4. MIGRATION PHASES — exactly 4 phases:
<div class="section-heading"><div class="sh-dot" style="background:#FF9900"></div>Recommended Migration Approach</div>
<div class="phases">
  <div class="phase-row"><div class="phase-num p1">1</div><div><div class="phase-title">Phase title (Weeks X-X)</div><div class="phase-desc">What happens in this phase.</div></div></div>
  <div class="phase-row"><div class="phase-num p2">2</div><div><div class="phase-title">Phase title (Weeks X-X)</div><div class="phase-desc">What happens in this phase.</div></div></div>
  <div class="phase-row"><div class="phase-num p3">3</div><div><div class="phase-title">Phase title (Weeks X-X)</div><div class="phase-desc">What happens in this phase.</div></div></div>
  <div class="phase-row"><div class="phase-num p4">4</div><div><div class="phase-title">Phase title (Weeks X-X)</div><div class="phase-desc">What happens in this phase.</div></div></div>
</div>

Base all content strictly on the on-premises and AWS descriptions provided. Be specific — use actual component names from the descriptions. Do not invent components that were not mentioned."""
