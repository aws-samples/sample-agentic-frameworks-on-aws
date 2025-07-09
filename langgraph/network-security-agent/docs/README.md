# Network Security Analysis Agent - Comprehensive Documentation

## Overview

The Network Security Analysis Agent is an advanced cybersecurity tool that leverages Amazon Bedrock's Claude-3 Sonnet model with LangChain integration to analyze network traffic logs and identify potential security threats. The system uses specialized analysis tools to detect data exfiltration, port scanning, suspicious connections, and other malicious activities.

## Architecture

### Core Components

1. **Bedrock Integration**: Direct integration with Amazon Bedrock for Claude-3 Sonnet access
2. **LangChain Framework**: Tool calling and agent orchestration
3. **Analysis Tools**: Specialized functions for different threat detection scenarios
4. **Data Processing**: Pandas-based network log analysis
5. **Reporting System**: Automated security report generation

### Agent Types

#### Production Agents (`agents/bedrock/`)

**bedrock_agent_with_tools.py** - The flagship implementation featuring:
- Full Amazon Bedrock + LangChain integration
- 6 specialized network analysis tools
- Tool calling agent with Claude-3 Sonnet
- Comprehensive threat detection capabilities
- Professional security reporting

**bedrock_network_agent.py** - Core implementation with:
- Amazon Bedrock + LangChain integration
- Statistical analysis and pattern detection
- Direct Claude interaction without tools
- Comprehensive security assessments

#### Demo Agents (`agents/demo/`)

**demo_agent_with_tools.py** - Demonstration version that:
- Simulates tool usage without AWS requirements
- Shows expected Claude analytical process
- Perfect for understanding system capabilities
- No cloud dependencies

**demo_bedrock_agent.py** - Bedrock simulation that:
- Demonstrates expected Bedrock agent output
- Shows analysis quality and format
- No AWS credentials required
- Educational purposes

## Analysis Tools

The `bedrock_agent_with_tools.py` includes 6 specialized analysis tools:

### 1. get_top_data_transfers
**Purpose**: Identify potential data exfiltration
- Analyzes largest data transfers by bytes
- Flags unusually large outbound transfers
- Helps detect data theft attempts

### 2. check_port_scanning
**Purpose**: Detect reconnaissance behavior
- Identifies IPs connecting to many different ports
- Configurable threshold for scanning detection
- Reveals potential attackers mapping networks

### 3. check_suspicious_ports
**Purpose**: Flag malicious port usage
- Monitors connections to known malicious ports (31337, 1337, 4444, etc.)
- Identifies backdoor and trojan communications
- Alerts on non-standard service usage

### 4. analyze_protocol_distribution
**Purpose**: Find protocol anomalies
- Analyzes TCP/UDP/other protocol usage patterns
- Detects unusual protocol distributions
- Identifies potential tunneling or covert channels

### 5. get_high_volume_ips
**Purpose**: Identify compromised endpoints
- Finds IPs with excessive connection volumes
- Uses percentile-based thresholds
- Helps identify compromised or malicious hosts

### 6. analyze_temporal_patterns
**Purpose**: Detect coordinated attacks
- Analyzes traffic timing patterns
- Identifies traffic spikes and anomalies
- Reveals potential coordinated attack campaigns

## Data Format

### Input Requirements

Network logs must be in CSV format with the following columns:

```csv
ConnectionID,Timestamp,InitiatorIP,ResponderIP,ResponderPort,Protocol,InitiatorBytes,ResponderBytes
```

**Column Descriptions:**
- `ConnectionID`: Unique identifier for each connection
- `Timestamp`: Unix timestamp of connection
- `InitiatorIP`: Source IP address
- `ResponderIP`: Destination IP address  
- `ResponderPort`: Destination port number
- `Protocol`: Network protocol (tcp, udp, etc.)
- `InitiatorBytes`: Bytes sent by initiator
- `ResponderBytes`: Bytes sent by responder

### Sample Data Structure

```csv
1,1625097600,192.168.1.100,203.0.113.1,443,tcp,1024,2048
2,1625097601,192.168.1.101,203.0.113.2,80,tcp,512,1024
```

## Security Analysis Capabilities

### Threat Detection

1. **Data Exfiltration**
   - Large transfer detection
   - Unusual outbound traffic patterns
   - Repeated large transfers

2. **Network Reconnaissance**
   - Port scanning identification
   - Host discovery attempts
   - Service enumeration

3. **Malicious Communications**
   - Suspicious port usage
   - Known malware ports
   - Backdoor communications

4. **Traffic Anomalies**
   - Protocol distribution analysis
   - Volume-based anomalies
   - Temporal pattern analysis

### Risk Assessment

The system provides risk scoring based on:
- Severity of detected threats
- Number of anomalies found
- Confidence levels of detections
- Potential impact assessment

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- Claude model access in Amazon Bedrock
- Proper IAM permissions for Bedrock

### Dependencies

```bash
pip install pandas>=2.0.0 boto3>=1.34.0 langchain-aws>=0.1.0 langchain>=0.1.0
```

### AWS Configuration

1. Configure AWS credentials:
```bash
aws configure
```

2. Ensure Bedrock access is enabled in your AWS account
3. Verify Claude model access in Bedrock console

## Usage Examples

### Quick Start - Demo Mode

```bash
cd agents/demo
python3 demo_agent_with_tools.py
```

### Production Usage

```bash
cd agents/bedrock
python3 bedrock_agent_with_tools.py
```

### Custom Analysis

```python
from bedrock_agent_with_tools import BedrockNetworkAgentWithTools

# Initialize agent
agent = BedrockNetworkAgentWithTools(region_name='us-east-1')

# Run analysis
report = agent.run_analysis('path/to/network_logs.csv')
```

## Output and Reporting

### Generated Files

1. **Security Reports** (`.txt` files)
   - Executive summary
   - Detailed findings
   - Risk assessment
   - Recommendations

2. **Statistics Files** (`.json` files)
   - Raw network statistics
   - Analysis metadata
   - Tool results

### Report Structure

```
NETWORK SECURITY ANALYSIS REPORT
Generated: [timestamp]
Analyzed by: Amazon Bedrock (Claude-3 Sonnet)

EXECUTIVE SUMMARY
[Brief overview of findings]

THREAT ASSESSMENT
- Critical Threats
- High Priority Issues
- Medium Priority Issues

DETAILED FINDINGS
- Data Exfiltration Indicators
- Port Scanning Activity
- Suspicious Connections
- Traffic Anomalies

SPECIFIC RECOMMENDATIONS
[Actionable security recommendations]

RISK SCORE
[Overall risk assessment 1-10]
```

## Customization

### Configurable Parameters

1. **Suspicious Ports List**
```python
suspicious_ports = [31337, 1337, 4444, 6666, 12345, 54321]
```

2. **Detection Thresholds**
```python
port_scan_threshold = 10  # Unique ports for scanning detection
volume_percentile = 0.9   # High-volume IP threshold
```

3. **Model Parameters**
```python
model_kwargs = {
    "max_tokens": 3000,
    "temperature": 0.1,
    "top_p": 0.9
}
```

### Adding Custom Tools

```python
@tool
def custom_analysis_tool(parameter: str) -> str:
    """Custom analysis function"""
    # Your analysis logic here
    return "Analysis results"
```

## Performance Considerations

### Scalability

- Handles datasets up to 100,000 connections efficiently
- Memory usage scales with dataset size
- Processing time: ~1-2 minutes per 10,000 connections

### Optimization Tips

1. **Data Preprocessing**
   - Clean data before analysis
   - Remove duplicate entries
   - Validate timestamp formats

2. **Tool Selection**
   - Use specific tools for targeted analysis
   - Combine tools for comprehensive assessment
   - Adjust thresholds based on network size

## Troubleshooting

### Common Issues

1. **AWS Credentials**
   - Ensure proper AWS configuration
   - Verify Bedrock access permissions
   - Check region availability

2. **Data Format**
   - Validate CSV column names
   - Check timestamp format (Unix timestamps)
   - Ensure numeric fields are properly formatted

3. **Memory Issues**
   - Process large datasets in chunks
   - Increase system memory if needed
   - Use data sampling for initial analysis

### Error Messages

- `"No network data loaded"`: Check file path and format
- `"Error calling Claude via Bedrock"`: Verify AWS credentials and Bedrock access
- `"Bedrock access failed"`: Check IAM permissions and model availability

## Security Considerations

### Data Privacy

- Network logs may contain sensitive information
- Ensure proper data handling procedures
- Consider data anonymization for testing

### Access Control

- Restrict access to analysis results
- Use proper IAM roles and policies
- Monitor Bedrock API usage

## Contributing

### Development Guidelines

1. Follow existing code structure
2. Add comprehensive docstrings
3. Include error handling
4. Test with sample data
5. Update documentation

### Testing

```bash
# Run demo versions for testing
python3 agents/demo/demo_agent_with_tools.py
python3 agents/demo/demo_bedrock_agent.py
```

## License and Support

This project is designed for cybersecurity professionals and researchers. For support and questions, refer to the main repository documentation.