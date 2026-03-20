#!/bin/bash

echo "=== AWS COST AUDIT ==="
echo "Date: $(date)"
echo ""

echo "1. CLOUDFRONT DISTRIBUTIONS:"
echo "Expected: 1 (E3IA5ZUL2HT0NT)"
aws cloudfront list-distributions --query 'DistributionList.Items[].{ID:Id,Status:Status,Origins:Origins.Items[0].DomainName}' --output table

echo ""
echo "2. EC2 INSTANCES:"
aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].{ID:InstanceId,Type:InstanceType,State:State.Name}' --output table

echo ""
echo "3. RDS INSTANCES:"
aws rds describe-db-instances --query 'DBInstances[].{ID:DBInstanceIdentifier,Class:DBInstanceClass,Status:DBInstanceStatus}' --output table

echo ""
echo "4. LOAD BALANCERS:"
aws elbv2 describe-load-balancers --query 'LoadBalancers[].{Name:LoadBalancerName,State:State.Code}' --output table

echo ""
echo "5. LAMBDA FUNCTIONS:"
aws lambda list-functions --query 'Functions[].{Name:FunctionName,Runtime:Runtime}' --output table

echo ""
echo "6. COST BY SERVICE (Last 30 days):"
aws ce get-cost-and-usage \
    --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE \
    --query 'ResultsByTime[0].Groups[?Metrics.BlendedCost.Amount>`0.01`].{Service:Keys[0],Cost:Metrics.BlendedCost.Amount}' \
    --output table