# Contributing to Network Security Analysis Agent

Thank you for your interest in contributing to the Network Security Analysis Agent! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Standards](#development-standards)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- AWS Account (for testing production features)
- Basic understanding of cybersecurity concepts
- Familiarity with LangChain and Amazon Bedrock

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/your-username/network-agent.git
cd network-agent
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/original-owner/network-agent.git
```

## Development Setup

### 1. Create Development Environment

```bash
# Create virtual environment
python3 -m venv dev-env
source dev-env/bin/activate  # On Windows: dev-env\Scripts\activate

# Install dependencies
pip install -r setup/requirements.txt

# Install development dependencies
pip install pytest black flake8 jupyter mypy
```

### 2. Configure AWS (Optional)

For testing production features:
```bash
aws configure
# Enter your AWS credentials and region
```

### 3. Verify Setup

```bash
# Test demo version (no AWS required)
cd agents/demo
python3 demo_agent_with_tools.py

# Test production version (AWS required)
cd ../bedrock
python3 bedrock_agent_with_tools.py
```

## Contributing Guidelines

### Types of Contributions

We welcome the following types of contributions:

1. **Bug Fixes** - Fix existing issues
2. **Feature Enhancements** - Improve existing functionality
3. **New Features** - Add new analysis tools or capabilities
4. **Documentation** - Improve or add documentation
5. **Testing** - Add or improve test coverage
6. **Performance** - Optimize code performance

### Areas for Contribution

#### High Priority
- Additional analysis tools for threat detection
- Support for new data formats (JSON, Parquet, etc.)
- Performance optimizations for large datasets
- Enhanced error handling and logging
- Integration with other security tools

#### Medium Priority
- Web interface for analysis results
- Real-time analysis capabilities
- Additional LLM provider support
- Automated report scheduling
- Custom alerting mechanisms

#### Low Priority
- Visualization improvements
- Additional export formats
- Mobile-friendly interfaces
- Multi-language support

## Pull Request Process

### 1. Create Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: New threat detection tool for DNS analysis

- Implement DNS tunneling detection
- Add tests for DNS analysis
- Update documentation with new tool usage"
```

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/examples if applicable
- Test results

### 5. PR Review Process

- Automated tests will run
- Code review by maintainers
- Address feedback if needed
- Merge after approval

## Issue Reporting

### Bug Reports

When reporting bugs, include:

```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.0]
- AWS region: [e.g., us-east-1]
- Package versions: [output of pip freeze]

**Additional Context**
Any other relevant information
```

### Feature Requests

For feature requests, include:

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## Development Standards

### Code Style

#### Python Style Guide

Follow PEP 8 with these specific guidelines:

```python
# Use descriptive variable names
network_connections = load_data('file.csv')  # Good
data = load_data('file.csv')                 # Avoid

# Function documentation
def analyze_port_scanning(df: pd.DataFrame, threshold: int = 10) -> dict:
    """
    Detect potential port scanning behavior in network data.
    
    Args:
        df: DataFrame containing network connection data
        threshold: Minimum unique ports to consider scanning
        
    Returns:
        Dictionary containing scanning analysis results
        
    Raises:
        ValueError: If threshold is less than 1
    """
    pass

# Class documentation
class NetworkAnalyzer:
    """
    Analyzes network traffic for security threats.
    
    This class provides methods for detecting various types of
    network-based security threats including port scanning,
    data exfiltration, and suspicious connections.
    
    Attributes:
        suspicious_ports: List of known malicious ports
        threshold_config: Configuration for detection thresholds
    """
    pass
```

#### Code Formatting

Use Black for code formatting:
```bash
black agents/ --line-length 88
```

Use flake8 for linting:
```bash
flake8 agents/ --max-line-length 88
```

### Testing Standards

#### Unit Tests

```python
import pytest
import pandas as pd
from agents.bedrock.bedrock_agent_with_tools import NetworkAnalysisTools

class TestNetworkAnalysisTools:
    
    @pytest.fixture
    def sample_data(self):
        """Create sample network data for testing"""
        return pd.DataFrame({
            'ConnectionID': [1, 2, 3],
            'Timestamp': [1625097600, 1625097601, 1625097602],
            'InitiatorIP': ['192.168.1.1', '192.168.1.2', '192.168.1.1'],
            'ResponderIP': ['203.0.113.1', '203.0.113.2', '203.0.113.3'],
            'ResponderPort': [80, 443, 22],
            'Protocol': ['tcp', 'tcp', 'tcp'],
            'InitiatorBytes': [1000, 2000, 500],
            'ResponderBytes': [2000, 3000, 1000]
        })
    
    def test_port_scanning_detection(self, sample_data):
        """Test port scanning detection functionality"""
        # Create temporary CSV file
        sample_data.to_csv('test_data.csv', index=False)
        
        # Initialize tools
        tools = NetworkAnalysisTools('test_data.csv')
        
        # Test port scanning detection
        result = tools.check_port_scanning(threshold=2)
        
        # Assertions
        assert isinstance(result, str)
        assert "port scanners" in result.lower()
        
        # Cleanup
        os.remove('test_data.csv')
```

#### Integration Tests

```python
def test_full_analysis_workflow():
    """Test complete analysis workflow"""
    # This test requires AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        pytest.skip("AWS credentials not available")
    
    agent = BedrockNetworkAgentWithTools()
    report = agent.run_analysis('data/network_logs.csv')
    
    assert isinstance(report, str)
    assert len(report) > 100
    assert "THREAT ASSESSMENT" in report
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def analyze_network_threats(data: pd.DataFrame, config: dict) -> dict:
    """
    Analyze network data for security threats.
    
    This function performs comprehensive analysis of network traffic
    to identify potential security threats including data exfiltration,
    port scanning, and suspicious connections.
    
    Args:
        data: DataFrame containing network connection logs with columns:
            - ConnectionID: Unique identifier for each connection
            - Timestamp: Unix timestamp of connection
            - InitiatorIP: Source IP address
            - ResponderIP: Destination IP address
            - ResponderPort: Destination port number
            - Protocol: Network protocol (tcp, udp, etc.)
            - InitiatorBytes: Bytes sent by initiator
            - ResponderBytes: Bytes sent by responder
        config: Configuration dictionary with analysis parameters:
            - port_scan_threshold: Minimum ports for scanning detection
            - volume_percentile: Threshold for high-volume detection
            - suspicious_ports: List of known malicious ports
    
    Returns:
        Dictionary containing analysis results with keys:
            - threats_detected: List of identified threats
            - risk_score: Overall risk assessment (1-10)
            - recommendations: List of recommended actions
            - statistics: Raw analysis statistics
    
    Raises:
        ValueError: If required columns are missing from data
        TypeError: If data is not a pandas DataFrame
        
    Example:
        >>> import pandas as pd
        >>> data = pd.read_csv('network_logs.csv')
        >>> config = {'port_scan_threshold': 10, 'volume_percentile': 0.9}
        >>> results = analyze_network_threats(data, config)
        >>> print(f"Risk Score: {results['risk_score']}")
    """
    pass
```

### Git Commit Standards

#### Commit Message Format

```
Type: Brief description (50 chars max)

Detailed explanation of changes (if needed).
Include motivation and context.

- Bullet points for multiple changes
- Reference issues with #123
- Break lines at 72 characters
```

#### Commit Types

- **Add**: New features or files
- **Fix**: Bug fixes
- **Update**: Modifications to existing features
- **Remove**: Deleted features or files
- **Refactor**: Code restructuring without functionality changes
- **Test**: Adding or modifying tests
- **Docs**: Documentation changes

#### Examples

```bash
# Good commit messages
git commit -m "Add: DNS tunneling detection tool

Implement new analysis tool to detect DNS tunneling attacks
by analyzing query patterns and response sizes.

- Add dns_tunneling_detector function
- Include tests for DNS analysis
- Update tool registry with new detector"

git commit -m "Fix: Handle missing timestamp columns gracefully

Resolve issue where analysis would crash when timestamp
column contains null values.

Fixes #42"

git commit -m "Update: Improve port scanning detection accuracy

Enhance port scanning algorithm to reduce false positives
by considering connection timing and success rates."
```

### Performance Guidelines

#### Code Optimization

```python
# Use vectorized operations with pandas
# Good
high_volume_ips = df.groupby('InitiatorIP')['TotalBytes'].sum()
high_volume_ips = high_volume_ips[high_volume_ips > threshold]

# Avoid
high_volume_ips = []
for ip in df['InitiatorIP'].unique():
    total_bytes = df[df['InitiatorIP'] == ip]['TotalBytes'].sum()
    if total_bytes > threshold:
        high_volume_ips.append(ip)
```

#### Memory Management

```python
# Process large datasets in chunks
def process_large_dataset(file_path: str, chunk_size: int = 10000):
    """Process large CSV files in chunks to manage memory usage"""
    results = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        chunk_result = analyze_chunk(chunk)
        results.append(chunk_result)
    
    return combine_results(results)
```

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Changelog updated
- [ ] Security review completed
- [ ] Performance benchmarks run

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

### Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Security Best Practices](https://python.org/dev/security/)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for contributing to the Network Security Analysis Agent!