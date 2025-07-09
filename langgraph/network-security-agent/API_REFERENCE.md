# API Reference

## Core Classes

### BedrockNetworkAgentWithTools

The main agent class that provides comprehensive network security analysis using Amazon Bedrock and specialized tools.

#### Constructor

```python
BedrockNetworkAgentWithTools(region_name='us-east-1')
```

**Parameters:**
- `region_name` (str): AWS region for Bedrock service. Default: 'us-east-1'

**Example:**
```python
agent = BedrockNetworkAgentWithTools(region_name='us-west-2')
```

#### Methods

##### run_analysis(csv_file)

Executes complete network security analysis using all available tools.

**Parameters:**
- `csv_file` (str): Path to CSV file containing network logs

**Returns:**
- `str`: Comprehensive security analysis report

**Example:**
```python
report = agent.run_analysis('data/network_logs.csv')
```

##### display_collected_stats(tools)

Displays network statistics after loading CSV data.

**Parameters:**
- `tools` (NetworkAnalysisTools): Initialized tools object

**Returns:**
- None (prints statistics to console)

---

### BedrockNetworkAgent

Core Bedrock agent without specialized tools for basic analysis.

#### Constructor

```python
BedrockNetworkAgent(region_name='us-east-1')
```

**Parameters:**
- `region_name` (str): AWS region for Bedrock service

#### Methods

##### extract_network_stats(csv_file)

Extracts comprehensive network statistics from CSV file.

**Parameters:**
- `csv_file` (str): Path to network logs CSV file

**Returns:**
- `dict`: Dictionary containing network statistics

**Example:**
```python
stats = agent.extract_network_stats('data/network_logs.csv')
```

##### analyze_with_claude(network_stats)

Sends network statistics to Claude for analysis.

**Parameters:**
- `network_stats` (dict): Network statistics dictionary

**Returns:**
- `str`: Claude's security analysis

##### run_analysis(csv_file)

Executes complete network analysis workflow.

**Parameters:**
- `csv_file` (str): Path to CSV file

**Returns:**
- `str`: Full analysis report

---

### NetworkAnalysisTools

Utility class containing specialized analysis tools.

#### Constructor

```python
NetworkAnalysisTools(csv_file)
```

**Parameters:**
- `csv_file` (str): Path to network logs CSV file

**Attributes:**
- `df` (pandas.DataFrame): Processed network data
- `suspicious_ports` (list): List of known malicious ports

---

## Analysis Tools

### @tool Functions

These are LangChain tools used by the agent for specialized analysis.

#### get_top_data_transfers(limit: int = 10) -> str

Identifies the largest data transfers to detect potential exfiltration.

**Parameters:**
- `limit` (int): Number of top transfers to return. Default: 10

**Returns:**
- `str`: Formatted report of top data transfers

**Example Output:**
```
Top 10 data transfers:
• 192.168.1.100 → 203.0.113.1:443 (2.75 MB, tcp)
• 192.168.1.101 → 203.0.113.2:80 (1.50 MB, tcp)
```

#### check_port_scanning(threshold: int = 10) -> str

Detects potential port scanning behavior.

**Parameters:**
- `threshold` (int): Minimum unique ports to consider scanning. Default: 10

**Returns:**
- `str`: Port scanning analysis results

**Example Output:**
```
Potential port scanners (≥10 unique ports):
• 192.168.1.100: 25 unique ports, 150 total connections
```

#### check_suspicious_ports() -> str

Checks for connections to known malicious ports.

**Returns:**
- `str`: Suspicious port connection analysis

**Monitored Ports:**
- 31337 (Elite/Leet)
- 1337 (Leet)
- 4444 (Metasploit)
- 6666 (IRC/Backdoor)
- 12345 (NetBus)
- 54321 (Back Orifice)

#### analyze_protocol_distribution() -> str

Analyzes network protocol usage patterns.

**Returns:**
- `str`: Protocol distribution analysis with anomaly detection

**Example Output:**
```
Protocol distribution analysis:
• TCP: 1500 connections (75.0%), 45.2 MB
• UDP: 500 connections (25.0%), 12.1 MB
```

#### get_high_volume_ips(threshold_percentile: float = 0.9) -> str

Identifies IPs with unusually high activity levels.

**Parameters:**
- `threshold_percentile` (float): Percentile threshold for high volume. Default: 0.9

**Returns:**
- `str`: High-volume IP analysis

#### analyze_temporal_patterns() -> str

Analyzes timing patterns in network traffic.

**Returns:**
- `str`: Temporal pattern analysis with anomaly detection

---

## Data Structures

### Network Log CSV Format

Required columns for input CSV files:

| Column | Type | Description |
|--------|------|-------------|
| ConnectionID | int | Unique connection identifier |
| Timestamp | int | Unix timestamp |
| InitiatorIP | str | Source IP address |
| ResponderIP | str | Destination IP address |
| ResponderPort | int | Destination port number |
| Protocol | str | Network protocol (tcp, udp, etc.) |
| InitiatorBytes | int | Bytes sent by initiator |
| ResponderBytes | int | Bytes sent by responder |

### Statistics Dictionary Structure

```python
{
    'overview': {
        'total_connections': int,
        'unique_source_ips': int,
        'unique_dest_ips': int,
        'time_span_hours': float,
        'total_bytes_mb': float,
        'avg_bytes_per_connection': float,
        'max_single_transfer_mb': float
    },
    'protocol_analysis': {
        'tcp': int,
        'udp': int,
        # ... other protocols
    },
    'port_analysis': {
        'top_ports': dict,
        'suspicious_port_connections': int,
        'uncommon_port_connections': int
    },
    'ip_analysis': {
        'top_source_ips': dict,
        'connections_per_ip': dict,
        'potential_scanners': dict
    },
    'data_transfer_analysis': {
        'large_transfers_count': int,
        'large_transfers_threshold_mb': float,
        'top_data_transfers': list
    },
    'temporal_analysis': {
        'connections_per_minute': dict,
        'peak_activity_time': str
    }
}
```

---

## Configuration Options

### Model Parameters

```python
model_kwargs = {
    "max_tokens": 3000,        # Maximum response length
    "temperature": 0.1,        # Randomness (0.0-1.0)
    "top_p": 0.9              # Nucleus sampling
}
```

### Detection Thresholds

```python
# Port scanning detection
port_scan_threshold = 10      # Unique ports for scanning

# High volume detection
volume_percentile = 0.9       # 90th percentile threshold

# Large transfer detection
large_transfer_percentile = 0.95  # 95th percentile threshold
```

### Suspicious Ports Configuration

```python
suspicious_ports = [
    31337,  # Elite/Leet
    1337,   # Leet
    4444,   # Metasploit default
    6666,   # IRC/Backdoor
    12345,  # NetBus
    54321   # Back Orifice
]
```

---

## Error Handling

### Common Exceptions

#### BedrockError
Raised when Bedrock service encounters issues.

```python
try:
    agent = BedrockNetworkAgentWithTools()
    report = agent.run_analysis('data.csv')
except Exception as e:
    print(f"Bedrock error: {e}")
```

#### DataFormatError
Raised when CSV data format is invalid.

```python
# Check for required columns
required_columns = [
    'ConnectionID', 'Timestamp', 'InitiatorIP', 
    'ResponderIP', 'ResponderPort', 'Protocol',
    'InitiatorBytes', 'ResponderBytes'
]
```

#### CredentialsError
Raised when AWS credentials are missing or invalid.

```python
import boto3
from botocore.exceptions import NoCredentialsError

try:
    client = boto3.client('bedrock-runtime')
except NoCredentialsError:
    print("AWS credentials not configured")
```

---

## Usage Examples

### Basic Usage

```python
from agents.bedrock.bedrock_agent_with_tools import BedrockNetworkAgentWithTools

# Initialize agent
agent = BedrockNetworkAgentWithTools(region_name='us-east-1')

# Run analysis
report = agent.run_analysis('data/network_logs.csv')

# Print results
print(report)
```

### Custom Configuration

```python
# Initialize with custom region
agent = BedrockNetworkAgentWithTools(region_name='eu-west-1')

# Access internal tools for custom analysis
from agents.bedrock.bedrock_agent_with_tools import NetworkAnalysisTools

tools = NetworkAnalysisTools('data/network_logs.csv')
top_transfers = tools.get_top_data_transfers(limit=5)
port_scan_results = tools.check_port_scanning(threshold=15)
```

### Batch Processing

```python
import os

agent = BedrockNetworkAgentWithTools()

# Process multiple files
log_files = ['data/logs_day1.csv', 'data/logs_day2.csv']

for log_file in log_files:
    if os.path.exists(log_file):
        report = agent.run_analysis(log_file)
        
        # Save individual reports
        output_file = f"report_{os.path.basename(log_file)}.txt"
        with open(output_file, 'w') as f:
            f.write(report)
```

---

## Return Values

### Analysis Report Format

```
NETWORK SECURITY ANALYSIS REPORT (WITH TOOLS)
Generated: 2024-01-15 10:30:00
Analyzed by: Amazon Bedrock (Claude-3 Sonnet) with Network Analysis Tools
================================================================================

[Executive Summary]
[Threat Assessment]
[Detailed Findings]
[Specific Recommendations]
[Risk Score]
```

### Generated Files

1. **bedrock_tools_report.txt** - Main security report
2. **bedrock_network_stats.json** - Raw statistics
3. **demo_tools_report.txt** - Demo version report
4. **demo_network_stats.json** - Demo statistics

---

## Integration Examples

### Custom Tool Integration

```python
from langchain.tools import tool

@tool
def custom_threat_detector(ip_address: str) -> str:
    """Custom threat detection for specific IP"""
    # Your custom logic here
    return f"Analysis results for {ip_address}"

# Add to agent tools
agent.tools.append(custom_threat_detector)
```

### External System Integration

```python
import requests

def send_alert(threat_level, message):
    """Send alert to external system"""
    if threat_level >= 8:
        requests.post('https://your-siem.com/alerts', {
            'level': threat_level,
            'message': message
        })

# Use after analysis
report = agent.run_analysis('data.csv')
if "Risk Score: 9" in report:
    send_alert(9, "Critical network threat detected")
```