# EchoKernel Examples

This directory contains example scripts demonstrating the capabilities of EchoKernel's agent system.

## Running the Examples

### Option 1: Install in Development Mode (Recommended)

From the root directory of the project:

```bash
pip install -e .
```

Then you can run examples from anywhere:

```bash
python examples/agent-routing.py
python examples/task-decomposer.py
python examples/agent-routing-with-memory.py
python examples/web-access-example.py
python examples/web-search-example.py
python examples/agent-logging-example.py
python examples/collaborative-agent-example.py
```

### Option 2: Run from Root Directory

Navigate to the project root and run:

```bash
python examples/agent-routing.py
python examples/task-decomposer.py
python examples/agent-routing-with-memory.py
python examples/web-access-example.py
python examples/web-search-example.py
python examples/agent-logging-example.py
python examples/collaborative-agent-example.py
```

### Option 3: Run from Examples Directory

The examples have been updated with path fixes, so you can run them directly from this directory:

```bash
cd examples
python agent-routing.py
python task-decomposer.py
python agent-routing-with-memory.py
python web-access-example.py
python web-search-example.py
python agent-logging-example.py
python collaborative-agent-example.py
```

## Available Examples

### agent-routing.py
Demonstrates a complex multi-agent system with:
- Specialist routing between different agent types
- Memory-enhanced agents (gracefully handles missing memory service)
- Looping execution with retries
- Task decomposition

### task-decomposer.py
Shows the TaskDecomposerAgent breaking down a complex task into subtasks and coordinating execution.

### agent-routing-with-memory.py
Full example showing how to set up the agent system with memory capabilities:
- Complete provider setup including embeddings and vector storage
- Memory-enhanced agents with context retention
- Shows how to enable/disable memory features

### web-access-example.py
Demonstrates the web access tool capabilities:
- **Safe web content retrieval** with rate limiting and URL validation
- **HTML content extraction** including title, text, and metadata
- **Error handling** for various HTTP status codes and network issues
- **Direct tool usage** and integration with EchoKernel
- **URL validation testing** showing security measures
- Shows how to register and use web access tools with AI agents

### web-search-example.py
Demonstrates the new search provider system:
- **DuckDuckGo search provider** (free, no API key required)
- **Google search provider** (requires API key and search engine ID)
- **Bing search provider** (requires API key)
- **WebAccess class integration** with different search providers
- **EchoKernel integration** with search tools
- **Provider configuration** and fallback mechanisms
- Shows how to use different search engines for web queries

### agent-logging-example.py
Demonstrates how to control agent logging behavior:
- **Three different methods** to enable/disable agent logging
- **Kernel constructor parameter** for explicit control
- **Environment variable configuration** for global settings
- **Side-by-side comparison** of logging enabled vs disabled
- Shows how agents run silently when logging is disabled
- Useful for production environments or cleaner output

### collaborative-agent-example.py
Demonstrates the new CollaborativeAgent for iterative workflows:
- **Editor-Writer collaboration** for content creation and refinement
- **Code Reviewer-Developer collaboration** for code improvement
- **Silent collaboration** with logging disabled for production use
- **Customizable stop phrases** to control when collaboration ends
- **Role-based prompts** that adapt to each agent's specialty
- Perfect for iterative improvement workflows and quality assurance

### novella-writer.py
Advanced example demonstrating multi-level task decomposition for creative writing:
- **7-level decomposition process** from prompt to complete novella
- **Specialized agents** for different writing tasks (design, character development, scene writing, etc.)
- **Quality assurance** with built-in review and editing process
- **Progressive refinement** where each level builds upon previous outputs
- Generates a complete 10-chapter novella with character development, plot arcs, and scene details
- Saves the final novella to `generated_novella.txt`

See `novella-writer-README.md` for detailed documentation of this example.

## Memory Setup

To use memory-enhanced agents, you need to:

1. **Configure Embedding Provider**: Uncomment the embedding provider setup in `agent-routing-with-memory.py`
2. **Configure Vector Storage**: Set up Qdrant or use in-memory storage
3. **Register Providers**: Uncomment the provider registration lines

Example configuration in `config.py`:
```python
# For Qdrant vector storage
QDRANT_URL = "your-qdrant-url"
QDRANT_COLLECTION_NAME = "your-collection-name"
QDRANT_API_KEY = "your-qdrant-api-key"
```

## Prerequisites

Make sure you have:
1. Set up your `config.py` file with API credentials
2. Installed the required dependencies (`pip install -r requirements.txt`)
3. Activated your virtual environment if using one
4. (Optional) Set up Qdrant or other vector storage for memory features 