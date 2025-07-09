# Installation Guide

## Quick Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd network-agent

# Run automated setup
cd setup
python3 setup_bedrock_agent.py
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r setup/requirements.txt

# Configure AWS credentials
aws configure
```

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended for large datasets)
- **Storage**: 1GB free space

### AWS Requirements

- **AWS Account** with active subscription
- **Amazon Bedrock** access enabled
- **Claude Model Access** in Bedrock console
- **IAM Permissions** for Bedrock operations

## Step-by-Step Installation

### 1. Python Environment Setup

#### Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv network-agent-env

# Activate virtual environment
# On Linux/macOS:
source network-agent-env/bin/activate
# On Windows:
network-agent-env\Scripts\activate

# Install dependencies
pip install -r setup/requirements.txt
```

#### Using System Python
```bash
pip install -r setup/requirements.txt
```

### 2. AWS Configuration

#### Method 1: AWS CLI Configuration
```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)
- Default output format (json)

#### Method 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Method 3: IAM Roles (EC2/Lambda)
If running on AWS infrastructure, use IAM roles instead of credentials.

### 3. Amazon Bedrock Setup

#### Enable Bedrock Access
1. Log into AWS Console
2. Navigate to Amazon Bedrock
3. Go to "Model access" in the left sidebar
4. Request access to Claude models:
   - Claude 3 Sonnet
   - Claude 3.5 Sonnet (if available)

#### Verify Model Access
```bash
# Test Bedrock access
python3 -c "
import boto3
client = boto3.client('bedrock', region_name='us-east-1')
models = client.list_foundation_models()
print('Bedrock access successful!')
"
```

### 4. Required IAM Permissions

Create an IAM policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## Verification

### Test Demo Version (No AWS Required)
```bash
cd agents/demo
python3 demo_agent_with_tools.py
```

Expected output:
```
🚀 Demo: Bedrock Agent with Network Analysis Tools
============================================================
This shows how Claude would use tools to analyze network data

🔍 Loading network data and initializing tools...
📊 Loaded [X] network connections
```

### Test Production Version (AWS Required)
```bash
cd agents/bedrock
python3 bedrock_agent_with_tools.py
```

Expected output:
```
🚀 Bedrock Network Agent with Tools
==================================================
🔍 Loading network data...
📊 Loaded [X] network connections
🤖 Starting Claude analysis with tools...
```

## Troubleshooting Installation

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python3 --version

# If Python 3.8+ not available, install it:
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.8

# macOS (using Homebrew):
brew install python@3.8

# Windows: Download from python.org
```

#### 2. Dependency Installation Failures
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output to see errors
pip install -v -r setup/requirements.txt

# For specific package issues:
pip install --no-cache-dir package-name
```

#### 3. AWS Credentials Issues
```bash
# Verify credentials are configured
aws sts get-caller-identity

# If command fails, reconfigure:
aws configure

# Check credentials file location:
# Linux/macOS: ~/.aws/credentials
# Windows: %USERPROFILE%\.aws\credentials
```

#### 4. Bedrock Access Issues
```bash
# Check if Bedrock is available in your region
aws bedrock list-foundation-models --region us-east-1

# Common regions with Bedrock:
# us-east-1, us-west-2, eu-west-1, ap-southeast-1
```

#### 5. Permission Errors
```bash
# Check current IAM user/role
aws sts get-caller-identity

# Test Bedrock permissions
aws bedrock list-foundation-models
```

### Error Messages and Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'boto3'` | Run `pip install boto3` |
| `NoCredentialsError` | Configure AWS credentials with `aws configure` |
| `AccessDenied` | Add Bedrock permissions to IAM user/role |
| `ModelNotFound` | Enable Claude model access in Bedrock console |
| `RegionNotSupported` | Use a supported region (us-east-1, us-west-2, etc.) |

## Advanced Installation Options

### Docker Installation
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY setup/requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "agents/bedrock/bedrock_agent_with_tools.py"]
```

### Development Installation
```bash
# Install in development mode
pip install -e .

# Install additional development dependencies
pip install pytest black flake8 jupyter
```

### Production Deployment
```bash
# Use production-grade WSGI server
pip install gunicorn

# Set environment variables
export AWS_DEFAULT_REGION=us-east-1
export PYTHONPATH=/path/to/network-agent

# Run with proper logging
python3 -u agents/bedrock/bedrock_agent_with_tools.py > analysis.log 2>&1
```

## Post-Installation

### 1. Prepare Sample Data
```bash
# Verify sample data exists
ls -la data/network_logs.csv

# If missing, create sample data or use your own network logs
```

### 2. Run First Analysis
```bash
# Start with demo version
cd agents/demo
python3 demo_agent_with_tools.py

# Then try production version
cd ../bedrock
python3 bedrock_agent_with_tools.py
```

### 3. Review Output
Check for generated files:
- `bedrock_tools_report.txt` - Main security report
- `bedrock_network_stats.json` - Raw statistics

## Getting Help

If you encounter issues during installation:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Test with demo version first
4. Check AWS service status
5. Review error logs carefully

For persistent issues, ensure you have:
- Correct Python version (3.8+)
- Valid AWS credentials
- Bedrock access enabled
- Proper IAM permissions
- Network connectivity to AWS services