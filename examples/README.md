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
```

### Option 2: Run from Root Directory

Navigate to the project root and run:

```bash
python examples/agent-routing.py
python examples/task-decomposer.py
python examples/agent-routing-with-memory.py
```

### Option 3: Run from Examples Directory

The examples have been updated with path fixes, so you can run them directly from this directory:

```bash
cd examples
python agent-routing.py
python task-decomposer.py
python agent-routing-with-memory.py
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