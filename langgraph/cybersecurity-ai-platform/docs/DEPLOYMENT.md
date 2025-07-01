# Deployment Guide

This guide covers different deployment options for the Cybersecurity AI Platform.

## 🚀 Deployment Options

### 1. Local Development

**Prerequisites:**
- Python 3.11+
- AWS CLI configured
- AWS Bedrock access

**Setup:**
```bash
# Clone and setup
git clone https://github.com/aws-samples/3P-Agentic-Frameworks.git
cd 3P-Agentic-Frameworks/cybersecurity-ai-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS
aws configure
export AWS_DEFAULT_REGION=us-east-1
```

**Run:**
```bash
# Interactive console
python3 examples/intent-classifier/interactive_security_console.py

# Workflow testing
python3 examples/langgraph-workflow/test_multiple_scenarios.py
```

### 2. Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for API (if using FastAPI)
EXPOSE 8000

# Default command
CMD ["python3", "examples/intent-classifier/interactive_security_console.py"]
```

**Build and run:**
```bash
# Build image
docker build -t cybersec-ai-platform .

# Run with AWS credentials
docker run -it \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  cybersec-ai-platform
```

### 3. AWS ECS Deployment

**Task Definition:**
```json
{
  "family": "cybersec-ai-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/cybersec-ai-task-role",
  "containerDefinitions": [
    {
      "name": "cybersec-ai",
      "image": "your-account.dkr.ecr.region.amazonaws.com/cybersec-ai-platform:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cybersec-ai-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 4. AWS Lambda Deployment

**For API endpoints:**

```python
# lambda_handler.py
import json
from core.intelligent_orchestrator import IntelligentOrchestrator

orchestrator = IntelligentOrchestrator()

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body'])
        query = body.get('query', '')
        
        # Process with orchestrator
        result = await orchestrator.process_user_query(query)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export AWS_DEFAULT_REGION=us-east-1

# Optional - if not using IAM roles
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Application settings
export LOG_LEVEL=INFO
export MAX_CONCURRENT_REQUESTS=10
```

### AWS IAM Permissions

**Minimum required permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            ]
        }
    ]
}
```

**Enhanced permissions for production:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

## 🏗️ Infrastructure as Code

### AWS CDK Deployment

```typescript
import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';

export class CybersecAiPlatformStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC
    const vpc = new ec2.Vpc(this, 'CybersecVpc', {
      maxAzs: 2
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'CybersecCluster', {
      vpc: vpc
    });

    // Task Role
    const taskRole = new iam.Role(this, 'CybersecTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
      ]
    });

    // Add Bedrock permissions
    taskRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeModel',
        'bedrock:InvokeModelWithResponseStream'
      ],
      resources: ['*']
    }));

    // Fargate Service
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'CybersecTaskDef', {
      memoryLimitMiB: 2048,
      cpu: 1024,
      taskRole: taskRole
    });

    taskDefinition.addContainer('cybersec-ai', {
      image: ecs.ContainerImage.fromRegistry('your-account.dkr.ecr.region.amazonaws.com/cybersec-ai-platform:latest'),
      portMappings: [{ containerPort: 8000 }],
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'cybersec-ai'
      })
    });
  }
}
```

### Terraform Deployment

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "cybersec_cluster" {
  name = "cybersec-ai-platform"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "cybersec_task" {
  family                   = "cybersec-ai-platform"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "cybersec-ai"
      image = "${var.ecr_repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.cybersec_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task_role" {
  name = "cybersec-ai-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Bedrock permissions
resource "aws_iam_role_policy" "bedrock_policy" {
  name = "bedrock-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      }
    ]
  })
}
```

## 📊 Monitoring & Logging

### CloudWatch Integration

```python
import logging
import boto3
from pythonjsonlogger import jsonlogger

# Configure structured logging
def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# Usage in agents
logger = setup_logging()

class NetworkSecurityAgent:
    async def assess_network_impact(self, event):
        logger.info("Starting network analysis", extra={
            "agent": "network",
            "source_ip": event.get("source_ip"),
            "destination_ip": event.get("destination_ip")
        })
        # ... analysis logic
```

### Metrics Collection

```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def put_metric(metric_name, value, unit='Count', namespace='CybersecAI'):
    cloudwatch.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
        ]
    )

# Usage
put_metric('AgentExecutions', 1)
put_metric('ResponseTime', response_time, 'Milliseconds')
```

## 🔒 Security Best Practices

### Network Security
- Use VPC with private subnets
- Configure security groups with minimal access
- Enable VPC Flow Logs

### Application Security
- No hardcoded credentials
- Use IAM roles instead of access keys
- Enable CloudTrail for API auditing
- Encrypt data in transit and at rest

### Monitoring
- Set up CloudWatch alarms
- Monitor Bedrock API usage
- Track error rates and latencies
- Enable AWS Config for compliance

## 🚀 Scaling Considerations

### Horizontal Scaling
- Use Application Load Balancer
- Deploy multiple ECS tasks
- Implement connection pooling
- Use Redis for session management

### Performance Optimization
- Cache frequent queries
- Implement request batching
- Use async processing
- Monitor Bedrock rate limits

### Cost Optimization
- Use Spot instances for non-critical workloads
- Implement auto-scaling policies
- Monitor Bedrock token usage
- Use reserved capacity when appropriate

## 🔧 Troubleshooting

### Common Issues

**Bedrock Access Denied:**
```bash
# Check IAM permissions
aws iam get-role-policy --role-name your-role --policy-name bedrock-policy

# Verify model access
aws bedrock list-foundation-models --region us-east-1
```

**Connection Timeouts:**
```python
# Increase timeout settings
import boto3
from botocore.config import Config

config = Config(
    read_timeout=60,
    connect_timeout=60,
    retries={'max_attempts': 3}
)
bedrock = boto3.client('bedrock-runtime', config=config)
```

**Memory Issues:**
- Increase ECS task memory
- Implement request queuing
- Use streaming responses for large outputs

For additional support, refer to the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/) and [LangChain documentation](https://python.langchain.com/).