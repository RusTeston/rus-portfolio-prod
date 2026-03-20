#!/bin/bash

echo "=== AWS COST CLEANUP SCRIPT ==="
echo "WARNING: This will delete expensive resources!"
echo ""

# CloudFront distributions to delete (keep only E3IA5ZUL2HT0NT)
DISTRIBUTIONS_TO_DELETE=(
    "E3M38C6J5BTIES"  # rustestonsite (legacy)
    "E27OLPVJXOAXU1"  # rusaiagent1 (duplicate)
    "E2CRYM24VDXR9E"  # rusaiagent1 (duplicate)
    "E2QQQLFRI66BOX"  # rus-arch-diagram-gen
    "E37J2GGHU5LAKA"  # rus-ai-agent
    "ER1LI6NUV37NB"   # project5-ha-webapp-alb
)

echo "1. DISABLING CLOUDFRONT DISTRIBUTIONS:"
for dist in "${DISTRIBUTIONS_TO_DELETE[@]}"; do
    echo "Disabling distribution: $dist"
    aws cloudfront get-distribution-config --id $dist --query 'DistributionConfig' > /tmp/config-$dist.json
    # Modify config to disable (set Enabled: false)
    jq '.Enabled = false' /tmp/config-$dist.json > /tmp/config-$dist-disabled.json
    
    # Get ETag for update
    ETAG=$(aws cloudfront get-distribution-config --id $dist --query 'ETag' --output text)
    
    # Update distribution to disable it
    aws cloudfront update-distribution --id $dist --distribution-config file:///tmp/config-$dist-disabled.json --if-match $ETAG
    echo "Distribution $dist disabled. Wait 15 minutes before deletion."
done

echo ""
echo "2. PROJECT 5 RESOURCES (High Cost):"
echo "EC2 Instances: i-02d1a81663cfe825f, i-07e699cc10e8532fd"
echo "RDS Database: project5-ha-webapp-database"
echo "Load Balancer: project5-ha-webapp-alb"
echo ""
echo "To stop Project 5 resources (saves ~$50-100/month):"
echo "aws ec2 stop-instances --instance-ids i-02d1a81663cfe825f i-07e699cc10e8532fd"
echo "aws rds stop-db-instance --db-instance-identifier project5-ha-webapp-database"
echo ""
echo "ESTIMATED MONTHLY SAVINGS:"
echo "- 6 CloudFront distributions: ~$30-60/month"
echo "- Project 5 EC2 instances: ~$30-50/month"
echo "- Project 5 RDS database: ~$20-40/month"
echo "- Load Balancer: ~$20/month"
echo "TOTAL SAVINGS: ~$100-170/month"