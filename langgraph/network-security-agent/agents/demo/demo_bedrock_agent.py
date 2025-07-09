import pandas as pd
import json
from datetime import datetime

class DemoBedrockNetworkAgent:
    """Demo version of Bedrock Network Agent - shows structure without requiring AWS credentials"""
    
    def __init__(self):
        self.suspicious_ports = [31337, 1337, 4444, 6666, 12345, 54321]
        self.common_ports = [80, 443, 22, 21, 25, 53, 110, 143, 993, 995, 7070, 8080, 9090]
    
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
    
    def simulate_claude_analysis(self, network_stats):
        """Simulate what Claude would analyze - shows the kind of insights an LLM would provide"""
        
        # This simulates the kind of analysis Claude would provide
        mock_claude_response = f"""
## EXECUTIVE SUMMARY
Analysis of {network_stats['overview']['total_connections']:,} network connections reveals significant security concerns. The network shows patterns consistent with potential data exfiltration activities, with unusually large data transfers averaging {network_stats['overview']['avg_bytes_per_connection']/1024:.1f} KB per connection.

## THREAT ASSESSMENT

### Critical Threats
- **Data Exfiltration Risk**: {network_stats['data_transfer_analysis']['large_transfers_count']} connections exceed the 95th percentile threshold ({network_stats['data_transfer_analysis']['large_transfers_threshold_mb']:.1f} MB), indicating potential unauthorized data movement
- **Concentrated Activity**: Only {network_stats['overview']['unique_source_ips']} unique source IPs generated all traffic, suggesting possible compromised endpoints

### High Priority Issues  
- **Large Volume Transfers**: Maximum single transfer of {network_stats['overview']['max_single_transfer_mb']:.1f} MB requires immediate investigation
- **Protocol Distribution**: {network_stats['protocol_analysis']} - UDP dominance may indicate tunneling or covert channels

### Medium Priority Issues
- **Port Usage Patterns**: Heavy reliance on port {max(network_stats['port_analysis']['top_ports'], key=network_stats['port_analysis']['top_ports'].get)} needs validation
- **Temporal Clustering**: Peak activity at {network_stats['temporal_analysis']['peak_activity_time']} suggests coordinated activity

## DETAILED FINDINGS

### Data Exfiltration Indicators
- **Volume Analysis**: {network_stats['overview']['total_bytes_mb']:.1f} MB transferred in {network_stats['overview']['time_span_hours']:.1f} hours
- **Transfer Pattern**: Large, consistent transfers suggest automated data extraction rather than normal user activity
- **Size Distribution**: 95th percentile threshold at {network_stats['data_transfer_analysis']['large_transfers_threshold_mb']:.1f} MB indicates systematic large file movement

### Port Scanning Activity
{"- **Scanning Detected**: Multiple IPs showing reconnaissance behavior" if any(count > 10 for count in network_stats['ip_analysis']['potential_scanners'].values()) else "- **No Port Scanning**: No clear scanning patterns detected"}

### Suspicious Connections
- **Suspicious Ports**: {network_stats['port_analysis']['suspicious_port_connections']} connections to known malicious ports
- **Uncommon Ports**: {network_stats['port_analysis']['uncommon_port_connections']} connections to non-standard ports

### Traffic Anomalies
- **Source Concentration**: {network_stats['overview']['unique_source_ips']} sources to {network_stats['overview']['unique_dest_ips']} destinations suggests potential lateral movement
- **Protocol Anomalies**: {list(network_stats['protocol_analysis'].keys())[0]} protocol dominance may indicate tunneling

## SPECIFIC RECOMMENDATIONS

1. **Immediate Investigation**: Review the top 5 largest data transfers, particularly connections exceeding {network_stats['data_transfer_analysis']['large_transfers_threshold_mb']:.1f} MB
2. **Source IP Analysis**: Investigate the {network_stats['overview']['unique_source_ips']} source IPs for signs of compromise, especially high-volume sources
3. **Data Loss Prevention**: Implement DLP controls to monitor and restrict large outbound transfers
4. **Network Segmentation**: Consider isolating high-volume source IPs pending investigation
5. **Continuous Monitoring**: Deploy real-time alerting for transfers exceeding normal baselines

## RISK SCORE
**Risk Score: 8/10 (High Risk)**

**Justification**: The combination of large data transfers, concentrated source activity, and high average transfer sizes strongly suggests potential data exfiltration. The {network_stats['overview']['avg_bytes_per_connection']/1024:.0f} KB average per connection is significantly above normal business traffic patterns. Immediate investigation and containment measures are recommended.
"""
        
        return mock_claude_response
    
    def run_analysis(self, csv_file):
        """Execute complete network analysis with simulated Claude response"""
        print("🔍 Extracting network statistics...")
        stats = self.extract_network_stats(csv_file)
        
        print("🤖 Simulating Claude analysis via Amazon Bedrock...")
        print("    (This shows what the real agent would produce)")
        claude_analysis = self.simulate_claude_analysis(stats)
        
        # Create comprehensive report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        full_report = f"""
NETWORK SECURITY ANALYSIS REPORT
Generated: {timestamp}
Analyzed by: Amazon Bedrock (Claude-3 Sonnet) - DEMO MODE
{'='*80}

{claude_analysis}

{'='*80}
RAW NETWORK STATISTICS
{'='*80}
{json.dumps(stats, indent=2, default=str)}
"""
        
        # Save outputs
        with open('demo_network_stats.json', 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        with open('demo_security_report.txt', 'w') as f:
            f.write(full_report)
        
        print("✅ Demo analysis complete!")
        print("📁 Files generated:")
        print("  - demo_network_stats.json")
        print("  - demo_security_report.txt")
        
        return full_report

# Usage example
if __name__ == "__main__":
    print("🚀 Demo Bedrock Network Security Agent")
    print("=" * 50)
    print("This demonstrates what the real Bedrock agent would produce")
    print("when connected to Claude via Amazon Bedrock.")
    print()
    
    agent = DemoBedrockNetworkAgent()
    report = agent.run_analysis('../../data/network_logs.csv')
    
    # Display key sections
    print("\n" + "="*80)
    print("DEMO CLAUDE SECURITY ANALYSIS")
    print("="*80)
    print(report)