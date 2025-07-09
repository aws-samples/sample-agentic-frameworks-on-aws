#!/usr/bin/env python3
"""
Setup script for Bedrock Network Security Agent
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("🔐 Checking AWS credentials...")
    
    # Check for AWS credentials
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_profile = os.getenv('AWS_PROFILE')
    
    if aws_access_key and aws_secret_key:
        print("✅ AWS credentials found in environment variables")
        return True
    elif aws_profile:
        print(f"✅ AWS profile found: {aws_profile}")
        return True
    else:
        print("⚠️  AWS credentials not found in environment")
        print("Please configure AWS credentials using one of these methods:")
        print("1. aws configure")
        print("2. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("3. Use IAM roles (if running on EC2)")
        return False

def test_bedrock_access():
    """Test Bedrock access"""
    print("🧪 Testing Bedrock access...")
    try:
        import boto3
        client = boto3.client('bedrock', region_name='us-east-1')
        # Try to list foundation models
        response = client.list_foundation_models()
        print("✅ Bedrock access confirmed!")
        return True
    except Exception as e:
        print(f"❌ Bedrock access failed: {e}")
        print("Make sure:")
        print("1. Your AWS account has Bedrock access enabled")
        print("2. You have proper IAM permissions for Bedrock")
        print("3. Claude models are enabled in your Bedrock console")
        return False

def main():
    print("🚀 Setting up Bedrock Network Security Agent...")
    print("="*50)
    
    # Install packages
    if not install_requirements():
        return False
    
    # Check AWS setup
    if not check_aws_credentials():
        print("⚠️  Continue with AWS setup, but agent may not work without proper credentials")
    
    # Test Bedrock
    if not test_bedrock_access():
        print("⚠️  Bedrock access test failed, but setup will continue")
    
    print("\n🎉 Setup complete!")
    print("\nTo run the agent:")
    print("python3 bedrock_network_agent.py")
    
    return True

if __name__ == "__main__":
    main()