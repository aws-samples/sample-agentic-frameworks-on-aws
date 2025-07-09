import pandas as pd
import json
from datetime import datetime
import boto3
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, SystemMessage

class BedrockNetworkAgent:
    def __init__(self, region_name='us-east-1'):
        self.suspicious_ports = [31337, 1337, 4444, 6666, 12345, 54321]
        self.common_ports = [80, 443, 22, 21, 25, 53, 110, 143, 993, 995, 7070, 8080, 9090]
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        
        # Initialize Claude via LangChain
        self.llm = ChatBedrock(
            client=self.bedrock_client,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens": 2000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
    
    def extract_network_stats(self, csv_file):
        """Extract comprehensive network statistics"""
        df = pd.read_csv(csv_file)
        
        # Preprocessing
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df['InitiatorBytes'] = df['InitiatorBytes'].fillna(0)
        df['ResponderBytes'] = df['ResponderBytes'].fillna(0)
        df['TotalBytes'] = df['InitiatorBytes'] + df['ResponderBytes']
        df['minute'] = df['timestamp'].dt.floor('min')
        
        # Display network statistics before LLM analysis
        print("\n📊 NETWORK STATISTICS EXTRACTED:")
        print("=" * 50)
        
        # 1. Bytes transferred per IP
        print("\n1. BYTES TRANSFERRED PER IP:")
        bytes_per_ip = df.groupby('InitiatorIP').agg({
            'TotalBytes': 'sum',
            'ConnectionID': 'count'
        }).rename(columns={'ConnectionID': 'Connections'})
        bytes_per_ip['TotalBytes_MB'] = bytes_per_ip['TotalBytes'] / 1024 / 1024
        print(bytes_per_ip.sort_values('TotalBytes', ascending=False).head(8))
        
        # 2. Connections per protocol
        print("\n2. CONNECTIONS PER PROTOCOL:")
        protocol_stats = df.groupby('Protocol').agg({
            'ConnectionID': 'count',
            'TotalBytes': 'sum'
        }).rename(columns={'ConnectionID': 'Connections'})
        protocol_stats['TotalBytes_MB'] = protocol_stats['TotalBytes'] / 1024 / 1024
        print(protocol_stats.sort_values('Connections', ascending=False))
        
        # 3. Connections per minute
        print("\n3. CONNECTIONS PER MINUTE (Top 10):")
        conn_per_min = df.groupby('minute').size().sort_values(ascending=False)
        print(conn_per_min.head(10))
        
        # 4. Repeated connections to same IP/port
        print("\n4. REPEATED CONNECTIONS TO SAME IP/PORT:")
        repeated = df.groupby(['InitiatorIP', 'ResponderIP', 'ResponderPort']).size().sort_values(ascending=False)
        repeated_filtered = repeated[repeated > 1]
        print(f"Total repeated connections: {len(repeated_filtered)}")
        if len(repeated_filtered) > 0:
            print("Top repeated connections:")
            print(repeated_filtered.head(10))
        
        print("\n" + "=" * 50)
        print("📤 Sending statistics to Claude for analysis...\n")
        
        # Calculate comprehensive statistics
        stats = {
            'overview': {
                'total_connections': len(df),
                'unique_source_ips': df['InitiatorIP'].nunique(),
                'unique_dest_ips': df['ResponderIP'].nunique(),
                'time_span_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600,
                'total_bytes_mb': df['TotalBytes'].sum() / 1024 / 1024,
                'avg_bytes_per_connection': df['TotalBytes'].mean(),
                'max_single_transfer_mb': df['TotalBytes'].max() / 1024 / 1024
            },
            
            'protocol_analysis': df['Protocol'].value_counts().to_dict(),
            
            'port_analysis': {
                'top_ports': df['ResponderPort'].value_counts().head(10).to_dict(),
                'suspicious_port_connections': len(df[df['ResponderPort'].isin(self.suspicious_ports)]),
                'uncommon_port_connections': len(df[~df['ResponderPort'].isin(self.common_ports)])
            },
            
            'ip_analysis': {
                'top_source_ips': df['InitiatorIP'].value_counts().head(5).to_dict(),
                'connections_per_ip': df.groupby('InitiatorIP').size().describe().to_dict(),
                'potential_scanners': df.groupby('InitiatorIP')['ResponderPort'].nunique().sort_values(ascending=False).head(5).to_dict()
            },
            
            'data_transfer_analysis': {
                'large_transfers_count': len(df[df['TotalBytes'] > df['TotalBytes'].quantile(0.95)]),
                'large_transfers_threshold_mb': df['TotalBytes'].quantile(0.95) / 1024 / 1024,
                'top_data_transfers': df.nlargest(5, 'TotalBytes')[['InitiatorIP', 'ResponderIP', 'ResponderPort', 'TotalBytes']].to_dict('records')
            },
            
            'temporal_analysis': {
                'connections_per_minute': df.groupby(df['timestamp'].dt.floor('min')).size().describe().to_dict(),
                'peak_activity_time': df.groupby(df['timestamp'].dt.floor('min')).size().idxmax().isoformat() if len(df) > 0 else None
            }
        }
        
        return stats
    
    def analyze_with_claude(self, network_stats):
        """Send network stats to Claude for analysis"""
        
        system_prompt = """You are a senior cybersecurity analyst specializing in network traffic analysis and threat detection. 
        You have extensive experience identifying attack patterns, data exfiltration, port scanning, and other malicious activities.
        Provide detailed, actionable security analysis based on network statistics."""
        
        human_prompt = f"""
Please analyze the following network traffic statistics and provide a comprehensive security assessment:

NETWORK STATISTICS:
{json.dumps(network_stats, indent=2, default=str)}

Please provide your analysis in the following format:

## EXECUTIVE SUMMARY
Brief overview of the network activity and key findings.

## THREAT ASSESSMENT
### Critical Threats
- List any critical security threats identified
### High Priority Issues  
- List high priority security concerns
### Medium Priority Issues
- List medium priority items for investigation

## DETAILED FINDINGS
### Data Exfiltration Indicators
- Analyze large data transfers and unusual patterns
### Port Scanning Activity
- Identify potential reconnaissance or scanning behavior
### Suspicious Connections
- Flag unusual IP/port combinations or protocols
### Traffic Anomalies
- Highlight any abnormal patterns in volume, timing, or behavior

## SPECIFIC RECOMMENDATIONS
Provide 3-5 specific, actionable recommendations for the security team.

## RISK SCORE
Provide an overall risk score (1-10) and justification.

Focus on practical, actionable insights that a security operations team can immediately act upon.
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error calling Claude via Bedrock: {str(e)}"
    
    def run_analysis(self, csv_file):
        """Execute complete network analysis"""
        print("🔍 Extracting network statistics...")
        stats = self.extract_network_stats(csv_file)
        
        print("🤖 Analyzing with Claude via Amazon Bedrock...")
        claude_analysis = self.analyze_with_claude(stats)
        
        # Create comprehensive report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        full_report = f"""
NETWORK SECURITY ANALYSIS REPORT
Generated: {timestamp}
Analyzed by: Amazon Bedrock (Claude-3 Sonnet)
{'='*80}

{claude_analysis}

{'='*80}
RAW NETWORK STATISTICS
{'='*80}
{json.dumps(stats, indent=2, default=str)}
"""
        
        # Save outputs
        with open('bedrock_network_stats.json', 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        with open('bedrock_security_report.txt', 'w') as f:
            f.write(full_report)
        
        print("✅ Analysis complete!")
        print("📁 Files generated:")
        print("  - bedrock_network_stats.json")
        print("  - bedrock_security_report.txt")
        
        return full_report

# Usage example
if __name__ == "__main__":
    try:
        # Initialize agent (make sure AWS credentials are configured)
        agent = BedrockNetworkAgent(region_name='us-east-1')
        
        # Run analysis
        report = agent.run_analysis('../../data/network_logs.csv')
        
        # Display report
        print("\n" + "="*80)
        print("CLAUDE SECURITY ANALYSIS")
        print("="*80)
        print(report)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. AWS credentials configured (aws configure)")
        print("2. Bedrock access enabled in your AWS account")
        print("3. Required packages: pip install langchain-aws boto3 pandas")