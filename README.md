# Multi-Agent AI System with LangGraph and LangSmith

A comprehensive multi-agent AI system built using LangGraph for agent orchestration and LangSmith for monitoring and debugging. Now includes **Document Intelligence** capabilities with local LLMs for privacy-preserving document processing.

## Features

- **Multi-Agent Architecture**: Coordinated agents with specialized roles
- **LangGraph Integration**: State-based agent workflows and graph execution
- **LangSmith Monitoring**: Real-time tracing and debugging capabilities
- **Document Intelligence**: Local document processing with Ollama + Phi-4
- **Privacy-First Processing**: On-premise document analysis with PII masking
- **Multi-Format Support**: PDFs, images, Word documents, and text files
- **Modular Design**: Easily extensible agent types and tools
- **Configuration Management**: Environment-based configuration
- **Comprehensive Examples**: Multiple use cases and scenarios

## New: Document Intelligence with Local LLMs 🆕

This system now includes advanced document intelligence capabilities powered by local LLMs:

- **Local Processing**: Ollama + Phi-4 for on-premise document analysis
- **Privacy Compliance**: Built-in PII masking for GDPR/HIPAA compliance
- **Multi-OCR Support**: Docling integration with multiple OCR engines
- **Context-Aware**: Intelligent pagination for limited context models
- **Vision Models**: Optional Moondream integration for complex layouts

### Quick Setup for Document Intelligence

```bash
# Windows
setup_document_intelligence.bat

# Linux/macOS
chmod +x setup_document_intelligence.sh
./setup_document_intelligence.sh
```

For detailed documentation, see [DOCUMENT_INTELLIGENCE.md](DOCUMENT_INTELLIGENCE.md)

## Project Structure

```text
Multi-Agent-AI-System-with-Lang/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── research_agent.py
│   │   ├── writing_agent.py
│   │   ├── review_agent.py
│   │   └── document_intelligence_agent.py  # 🆕 Local document processing
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search_tools.py
│   │   └── file_tools.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── content_creation.py
│   │   ├── research_workflow.py
│   │   └── document_intelligence_workflow.py  # 🆕 Document processing workflow
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py
│   └── main.py
├── examples/
│   ├── basic_multi_agent.py
│   ├── content_pipeline.py
│   ├── research_analysis.py
│   └── document_intelligence_local_llm.py  # 🆕 Document intelligence demo
├── tests/
│   ├── test_agents.py
│   └── test_workflows.py
├── documents/  # 🆕 Document upload directory
├── extracted/  # 🆕 Extracted data directory
├── requirements.txt
├── .env.example
├── setup_document_intelligence.sh  # 🆕 Unix setup script
├── setup_document_intelligence.bat  # 🆕 Windows setup script
├── DOCUMENT_INTELLIGENCE.md  # 🆕 Detailed documentation
└── README.md
```

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd Multi-Agent-AI-System-with-Lang
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Basic Example**
   ```bash
   python src/main.py
   ```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (true/false)
- `LANGCHAIN_API_KEY`: Your LangSmith API key
- `LANGCHAIN_PROJECT`: LangSmith project name

### Agent Configuration

Agents can be configured through the `config/settings.py` file to customize:
- Model parameters
- Agent personas and instructions
- Tool availability
- Workflow routing

## Architecture

### Agents

- **ResearchAgent**: Specializes in information gathering and analysis
- **WritingAgent**: Handles content creation and editing
- **ReviewAgent**: Performs quality assurance and validation
- **DocumentIntelligenceAgent**: 🆕 Processes documents with local LLMs for privacy-preserving extraction

### Workflows

- **Content Creation Pipeline**: Research → Write → Review
- **Research Analysis**: Multi-source information synthesis
- **Collaborative Decision Making**: Agent consensus mechanisms

### Tools

- **Search Tools**: Web search, document retrieval
- **File Tools**: File operations, content management
- **Communication Tools**: Inter-agent messaging

## Examples

### Basic Multi-Agent Interaction

```python
from src.workflows.content_creation import ContentCreationWorkflow

workflow = ContentCreationWorkflow()
result = workflow.run("Write an article about AI trends")
print(result)
```

### Document Intelligence with Local LLMs 🆕

```python
from src.workflows import process_document_with_local_llm

# Process a document with local Phi-4 model
result = process_document_with_local_llm(
    document_path="invoice.pdf",
    use_vision=False,
    enable_pii_masking=True
)

print(f"Document Type: {result['document_type']}")
print(f"Extracted Data: {result['extracted_data']}")
```

### Custom Agent Creation

```python
from src.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CustomAgent",
            role="Specialized Task Handler"
        )
    
    def process(self, state):
        # Custom logic here
        return state
```

## Monitoring with LangSmith

LangSmith provides comprehensive monitoring:
- Real-time execution traces
- Performance metrics
- Error tracking
- Agent interaction visualization

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
