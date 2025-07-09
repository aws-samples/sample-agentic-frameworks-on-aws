import pandas as pd
import json
from datetime import datetime
import boto3
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

class NetworkAnalysisTools:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], unit='s')
        self.df['InitiatorBytes'] = self.df['InitiatorBytes'].fillna(0)
        self.df['ResponderBytes'] = self.df['ResponderBytes'].fillna(0)
        self.df['TotalBytes'] = self.df['InitiatorBytes'] + self.df['ResponderBytes']
        self.suspicious_ports = [31337, 1337, 4444, 6666, 12345, 54321]

# Global variable to store the data
network_data = None

@tool
def get_top_data_transfers(limit: int = 10) -> str:
    """Get the top data transfers by bytes. Use this to identify potential data exfiltration."""
    if network_data is None:
        return "No network data loaded"
    
    top_transfers = network_data.df.nlargest(limit, 'TotalBytes')[
        ['InitiatorIP', 'ResponderIP', 'ResponderPort', 'TotalBytes', 'Protocol']
    ]
    
    result = f"Top {limit} data transfers:\n"
    for _, row in top_transfers.iterrows():
        mb_size = row['TotalBytes'] / 1024 / 1024
        result += f"• {row['InitiatorIP']} → {row['ResponderIP']}:{row['ResponderPort']} ({mb_size:.2f} MB, {row['Protocol']})\n"
    
    return result

@tool
def check_port_scanning(threshold: int = 10) -> str:
    """Check for potential port scanning behavior. Returns IPs connecting to many different ports."""
    if network_data is None:
        return "No network data loaded"
    
    port_counts = network_data.df.groupby('InitiatorIP')['ResponderPort'].nunique()
    scanners = port_counts[port_counts >= threshold]
    
    if len(scanners) == 0:
        return f"No port scanning detected (threshold: {threshold} unique ports)"
    
    result = f"Potential port scanners (≥{threshold} unique ports):\n"
    for ip, port_count in scanners.sort_values(ascending=False).items():
        conn_count = len(network_data.df[network_data.df['InitiatorIP'] == ip])
        result += f"• {ip}: {port_count} unique ports, {conn_count} total connections\n"
    
    return result

@tool
def check_suspicious_ports() -> str:
    """Check for connections to known suspicious ports (31337, 1337, 4444, etc.)."""
    if network_data is None:
        return "No network data loaded"
    
    suspicious_conns = network_data.df[network_data.df['ResponderPort'].isin(network_data.suspicious_ports)]
    
    if len(suspicious_conns) == 0:
        return "No connections to suspicious ports detected"
    
    result = f"Suspicious port connections detected ({len(suspicious_conns)} total):\n"
    for _, row in suspicious_conns.iterrows():
        result += f"• {row['InitiatorIP']} → {row['ResponderIP']}:{row['ResponderPort']} ({row['Protocol']})\n"
    
    return result

@tool
def analyze_protocol_distribution() -> str:
    """Analyze the distribution of network protocols and identify anomalies."""
    if network_data is None:
        return "No network data loaded"
    
    protocol_stats = network_data.df.groupby('Protocol').agg({
        'ConnectionID': 'count',
        'TotalBytes': 'sum'
    }).rename(columns={'ConnectionID': 'Connections'})
    
    total_connections = len(network_data.df)
    result = "Protocol distribution analysis:\n"
    
    for protocol, row in protocol_stats.iterrows():
        percentage = (row['Connections'] / total_connections) * 100
        mb_transferred = row['TotalBytes'] / 1024 / 1024
        result += f"• {protocol.upper()}: {row['Connections']} connections ({percentage:.1f}%), {mb_transferred:.1f} MB\n"
    
    # Check for anomalies
    if 'udp' in protocol_stats.index and protocol_stats.loc['udp', 'Connections'] > total_connections * 0.6:
        result += "\n⚠️  ANOMALY: UDP traffic dominance may indicate tunneling or covert channels\n"
    
    return result

@tool
def get_high_volume_ips(threshold_percentile: float = 0.9) -> str:
    """Get IPs with unusually high connection volumes or data transfers."""
    if network_data is None:
        return "No network data loaded"
    
    ip_stats = network_data.df.groupby('InitiatorIP').agg({
        'ConnectionID': 'count',
        'TotalBytes': 'sum'
    }).rename(columns={'ConnectionID': 'Connections'})
    
    conn_threshold = ip_stats['Connections'].quantile(threshold_percentile)
    bytes_threshold = ip_stats['TotalBytes'].quantile(threshold_percentile)
    
    high_volume = ip_stats[
        (ip_stats['Connections'] > conn_threshold) | 
        (ip_stats['TotalBytes'] > bytes_threshold)
    ]
    
    if len(high_volume) == 0:
        return f"No high-volume IPs detected (>{threshold_percentile*100}th percentile)"
    
    result = f"High-volume IPs (>{threshold_percentile*100}th percentile):\n"
    for ip, row in high_volume.sort_values('TotalBytes', ascending=False).iterrows():
        mb_transferred = row['TotalBytes'] / 1024 / 1024
        result += f"• {ip}: {row['Connections']} connections, {mb_transferred:.1f} MB transferred\n"
    
    return result

@tool
def analyze_temporal_patterns() -> str:
    """Analyze temporal patterns in network traffic to identify suspicious timing."""
    if network_data is None:
        return "No network data loaded"
    
    # Connections per minute
    conn_per_min = network_data.df.groupby(network_data.df['Timestamp'].dt.floor('min')).size()
    
    result = "Temporal analysis:\n"
    result += f"• Time span: {network_data.df['Timestamp'].min()} to {network_data.df['Timestamp'].max()}\n"
    result += f"• Peak activity: {conn_per_min.max()} connections at {conn_per_min.idxmax()}\n"
    result += f"• Average per minute: {conn_per_min.mean():.1f} connections\n"
    
    # Check for suspicious patterns
    if conn_per_min.max() > conn_per_min.mean() + 2 * conn_per_min.std():
        result += "\n⚠️  ANOMALY: Significant traffic spikes detected - possible coordinated activity\n"
    
    return result

class BedrockNetworkAgentWithTools:
    def __init__(self, region_name='us-east-1'):
        # Initialize Bedrock client
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        
        # Initialize Claude via LangChain
        self.llm = ChatBedrock(
            client=self.bedrock_client,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens": 3000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        # Define tools
        self.tools = [
            get_top_data_transfers,
            check_port_scanning,
            check_suspicious_ports,
            analyze_protocol_distribution,
            get_high_volume_ips,
            analyze_temporal_patterns
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior cybersecurity analyst with access to network analysis tools. 
            Use the available tools to thoroughly investigate network traffic for security threats.
            
            Your analysis should focus on:
            1. Data exfiltration indicators
            2. Port scanning activities  
            3. Suspicious connections
            4. Protocol anomalies
            5. Temporal attack patterns
            
            Use multiple tools to build a comprehensive security assessment."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def run_analysis(self, csv_file):
        """Execute complete network analysis using tools"""
        global network_data
        
        print("🔍 Loading network data...")
        network_data = NetworkAnalysisTools(csv_file)
        
        print(f"📊 Loaded {len(network_data.df)} network connections")
        
        # Display collected statistics
        self.display_collected_stats(network_data)
        
        print("🤖 Starting Claude analysis with tools...\n")
    
    def display_collected_stats(self, tools):
        """Display network statistics after reading CSV"""
        print("\n📊 COLLECTED NETWORK STATISTICS:")
        print("=" * 50)
        
        # 1. Bytes transferred per IP
        print("\n1. BYTES TRANSFERRED PER IP:")
        bytes_per_ip = tools.df.groupby('InitiatorIP').agg({
            'TotalBytes': 'sum',
            'ConnectionID': 'count'
        }).rename(columns={'ConnectionID': 'Connections'})
        bytes_per_ip['TotalBytes_MB'] = bytes_per_ip['TotalBytes'] / 1024 / 1024
        print(bytes_per_ip.sort_values('TotalBytes', ascending=False).head(8))
        
        # 2. Connections per protocol
        print("\n2. CONNECTIONS PER PROTOCOL:")
        protocol_stats = tools.df.groupby('Protocol').agg({
            'ConnectionID': 'count',
            'TotalBytes': 'sum'
        }).rename(columns={'ConnectionID': 'Connections'})
        protocol_stats['TotalBytes_MB'] = protocol_stats['TotalBytes'] / 1024 / 1024
        print(protocol_stats.sort_values('Connections', ascending=False))
        
        # 3. Connections per minute
        print("\n3. CONNECTIONS PER MINUTE (Top 10):")
        conn_per_min = tools.df.groupby(tools.df['Timestamp'].dt.floor('min')).size().sort_values(ascending=False)
        print(conn_per_min.head(10))
        
        # 4. Repeated connections to same IP/port
        print("\n4. REPEATED CONNECTIONS TO SAME IP/PORT:")
        repeated = tools.df.groupby(['InitiatorIP', 'ResponderIP', 'ResponderPort']).size().sort_values(ascending=False)
        repeated_filtered = repeated[repeated > 1]
        print(f"Total repeated connections: {len(repeated_filtered)}")
        if len(repeated_filtered) > 0:
            print("Top repeated connections:")
            print(repeated_filtered.head(10))
        
        print("\n" + "=" * 50)
        
        # Run agent analysis
        analysis_prompt = """
        Analyze the loaded network traffic data for security threats. Use all available tools to:
        
        1. Identify the largest data transfers that could indicate exfiltration
        2. Check for port scanning behavior
        3. Look for connections to suspicious ports
        4. Analyze protocol distribution for anomalies
        5. Find high-volume IP addresses
        6. Examine temporal patterns for coordinated attacks
        
        Provide a comprehensive security report with risk assessment and specific recommendations.
        """
        
        try:
            result = self.agent_executor.invoke({"input": analysis_prompt})
            
            # Save report
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_report = f"""
NETWORK SECURITY ANALYSIS REPORT (WITH TOOLS)
Generated: {timestamp}
Analyzed by: Amazon Bedrock (Claude-3 Sonnet) with Network Analysis Tools
{'='*80}

{result['output']}
"""
            
            with open('bedrock_tools_report.txt', 'w') as f:
                f.write(full_report)
            
            print("\n✅ Analysis complete!")
            print("📁 Report saved: bedrock_tools_report.txt")
            
            return result['output']
            
        except Exception as e:
            return f"Error during analysis: {str(e)}"

# Usage example
if __name__ == "__main__":
    try:
        print("🚀 Bedrock Network Agent with Tools")
        print("="*50)
        
        # Initialize agent
        agent = BedrockNetworkAgentWithTools(region_name='us-east-1')
        
        # Run analysis
        report = agent.run_analysis('../../data/network_logs.csv')
        
        print("\n" + "="*80)
        print("CLAUDE SECURITY ANALYSIS (WITH TOOLS)")
        print("="*80)
        print(report)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. AWS credentials configured")
        print("2. Bedrock access enabled")
        print("3. Required packages: pip install langchain-aws boto3 pandas")