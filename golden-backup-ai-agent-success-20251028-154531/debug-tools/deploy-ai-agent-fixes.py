#!/usr/bin/env python3
"""
Deploy AI Agent fixes to live Lambda functions
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def create_deployment_package(function_name, source_file):
    """Create deployment package for Lambda function"""
    
    zip_filename = f"{function_name}-deployment-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        zip_file.write(source_file, f"{function_name}.py")
    
    print(f"✅ Created deployment package: {zip_filename}")
    return zip_filename

def backup_current_function(lambda_client, function_name):
    """Backup current Lambda function code"""
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        code_url = response['Code']['Location']
        
        backup_filename = f"{function_name}-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
        
        # Download current code
        import urllib.request
        urllib.request.urlretrieve(code_url, backup_filename)
        
        print(f"✅ Backed up current function: {backup_filename}")
        return backup_filename
        
    except Exception as e:
        print(f"⚠️  Could not backup {function_name}: {e}")
        return None

def deploy_function(lambda_client, function_name, zip_file):
    """Deploy updated function code"""
    
    try:
        with open(zip_file, 'rb') as f:
            zip_content = f.read()
        
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Deployed {function_name} successfully")
        print(f"   Version: {response['Version']}")
        print(f"   Last Modified: {response['LastModified']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to deploy {function_name}: {e}")
        return False

def main():
    """Main deployment function"""
    
    print("🚀 AI Agent Fix Deployment")
    print("=" * 50)
    
    # AWS setup
    try:
        lambda_client = boto3.client('lambda')
        print("✅ Connected to AWS Lambda")
    except Exception as e:
        print(f"❌ AWS connection failed: {e}")
        return
    
    # Function mappings
    functions_to_deploy = [
        {
            'name': 'AgentOrchestratorFunction',
            'source': 'AgentOrchestratorFunction-FIXED.py'
        },
        {
            'name': 'RetrieveDocumentsFunction', 
            'source': 'RetrieveDocumentsFunction-FIXED.py'
        }
    ]
    
    deployed_functions = []
    backup_files = []
    
    for func in functions_to_deploy:
        print(f"\n📦 Processing {func['name']}...")
        
        # Check if source file exists
        if not os.path.exists(func['source']):
            print(f"❌ Source file not found: {func['source']}")
            continue
        
        # Backup current function
        backup_file = backup_current_function(lambda_client, func['name'])
        if backup_file:
            backup_files.append(backup_file)
        
        # Create deployment package
        zip_file = create_deployment_package(func['name'], func['source'])
        
        # Deploy function
        if deploy_function(lambda_client, func['name'], zip_file):
            deployed_functions.append(func['name'])
        
        # Cleanup deployment package
        os.remove(zip_file)
    
    # Summary
    print(f"\n📊 Deployment Summary")
    print("=" * 50)
    print(f"✅ Successfully deployed: {len(deployed_functions)} functions")
    for func in deployed_functions:
        print(f"   - {func}")
    
    if backup_files:
        print(f"\n💾 Backup files created:")
        for backup in backup_files:
            print(f"   - {backup}")
    
    print(f"\n🧪 Next Steps:")
    print("1. Test the live AI agent with pillar queries")
    print("2. Monitor CloudWatch logs for enhanced queries")
    print("3. Verify 6-pillar responses")
    
    if deployed_functions:
        print(f"\n🎯 Test URLs:")
        print("Visit your AI agent and try these queries:")
        print("- 'How many pillars are in the Well-Architected Framework?'")
        print("- 'What are the six pillars?'")
        print("- 'Tell me about the sustainability pillar'")

if __name__ == "__main__":
    main()