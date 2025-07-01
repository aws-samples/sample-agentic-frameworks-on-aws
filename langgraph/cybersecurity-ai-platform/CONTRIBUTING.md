# Contributing Guidelines

We welcome contributions to the Cybersecurity AI Platform! This document provides guidelines for contributing to this AWS sample project.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** - Search for similar issues before creating new ones
2. **Use issue templates** - Follow the provided templates when available
3. **Provide details** - Include steps to reproduce, expected vs actual behavior
4. **Include environment info** - AWS region, Python version, dependencies

### Suggesting Enhancements

1. **Check roadmap** - Review existing feature requests and roadmap
2. **Describe the use case** - Explain the business value and user benefit
3. **Provide examples** - Include mockups, code samples, or detailed descriptions

### Code Contributions

#### Prerequisites

- AWS Account with Bedrock access
- Python 3.11+
- Git knowledge
- Understanding of multi-agent AI systems

#### Development Setup

1. **Fork the repository**
```bash
git clone https://github.com/YOUR_USERNAME/3P-Agentic-Frameworks.git
cd 3P-Agentic-Frameworks/cybersecurity-ai-platform
```

2. **Create development environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

3. **Configure AWS credentials**
```bash
aws configure
export AWS_DEFAULT_REGION=us-east-1
```

#### Making Changes

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Follow coding standards**
   - Use Python type hints
   - Follow PEP 8 style guide
   - Add docstrings to functions and classes
   - Include error handling

3. **Test your changes**
```bash
# Test intent classifier
python3 examples/intent-classifier/interactive_security_console.py

# Test LangGraph workflow
python3 examples/langgraph-workflow/test_multiple_scenarios.py
```

4. **Update documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update architecture diagrams if applicable

#### Code Style Guidelines

**Python Code Style:**
```python
# Good
async def analyze_threat(self, event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze security threat using AI agent.
    
    Args:
        event: Security event data containing IPs, protocols, etc.
        
    Returns:
        Dict containing threat analysis results
    """
    try:
        result = await self.agent.invoke({"input": query})
        return self._process_result(result)
    except Exception as e:
        logger.error(f"Threat analysis failed: {e}")
        return {"error": str(e)}
```

**Agent Implementation:**
- Each agent should be self-contained
- Use proper error handling
- Include comprehensive logging
- Follow the established agent pattern

**Tool Functions:**
- Keep tools focused and single-purpose
- Use descriptive names and docstrings
- Handle edge cases gracefully

#### Pull Request Process

1. **Ensure tests pass**
   - Test both implementation approaches
   - Verify AWS Bedrock integration works
   - Check error handling

2. **Update documentation**
   - README.md changes if needed
   - Code comments and docstrings
   - Architecture documentation

3. **Create pull request**
   - Use descriptive title and description
   - Reference related issues
   - Include testing instructions

4. **Address review feedback**
   - Respond to reviewer comments
   - Make requested changes
   - Update tests if needed

## 🏗️ Architecture Guidelines

### Adding New Agents

When adding new AI agents:

1. **Follow the agent pattern**
```python
class NewAgent:
    def __init__(self):
        self.bedrock_client = BedrockLLMClient()
        self.agent = self._create_agent()
    
    async def analyze_something(self, event: Dict) -> Dict:
        # Implementation
        pass
    
    def _create_agent(self):
        # Agent creation with tools
        pass
```

2. **Create appropriate tools**
   - Single-purpose functions
   - Clear descriptions
   - Proper error handling

3. **Update orchestrators**
   - Add to both intent-based and LangGraph
   - Update routing logic
   - Add to agent mappings

### Modifying Orchestration

**Intent-Based Changes:**
- Update `intent_parser_agent.py` for new intents
- Modify `intelligent_orchestrator.py` for routing
- Update console interface if needed

**LangGraph Changes:**
- Modify state definitions
- Update workflow nodes and edges
- Test state transitions

## 🧪 Testing Guidelines

### Manual Testing

1. **Intent Classifier Testing**
```bash
# Test various query types
analyze Check network security for IP 192.168.1.45
analyze SQL injection attack on web server
simulate apt_campaign
```

2. **LangGraph Testing**
```bash
# Test workflow scenarios
python3 examples/langgraph-workflow/test_multiple_scenarios.py
```

### Integration Testing

- Test AWS Bedrock connectivity
- Verify agent tool functionality
- Check error handling paths
- Validate output formats

## 📋 Code Review Checklist

**Functionality:**
- [ ] Code works as intended
- [ ] Handles edge cases and errors
- [ ] Follows established patterns
- [ ] Integrates properly with existing code

**Code Quality:**
- [ ] Follows Python style guidelines
- [ ] Includes proper type hints
- [ ] Has comprehensive docstrings
- [ ] Uses appropriate logging

**Documentation:**
- [ ] README updated if needed
- [ ] Code is self-documenting
- [ ] Architecture docs updated
- [ ] Examples provided

**Security:**
- [ ] No hardcoded credentials
- [ ] Proper error handling
- [ ] Input validation where needed
- [ ] Follows AWS security best practices

## 🚀 Release Process

1. **Version Updates**
   - Update version numbers
   - Update CHANGELOG.md
   - Tag releases appropriately

2. **Documentation**
   - Ensure all docs are current
   - Update examples if needed
   - Verify installation instructions

3. **Testing**
   - Full integration testing
   - Performance validation
   - Security review

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **Discussions** - For questions and general discussion
- **AWS Documentation** - For Bedrock-specific questions
- **Community** - Join the AWS AI/ML community

## 🏷️ Labels and Tags

Use appropriate labels for issues and PRs:
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed

Thank you for contributing to the Cybersecurity AI Platform!