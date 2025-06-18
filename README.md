# EchoKernel

EchoKernel is a flexible and extensible Python framework for building AI-powered applications. It provides a modular architecture for working with various language models, embedding providers, and vector storage solutions, making it easy to create sophisticated AI applications with tool integration capabilities.

## Features

- 🔌 **Modular Provider System**: Easily switch between different AI providers (Azure OpenAI, OpenAI)
- 🛠️ **Tool Integration**: Register and use custom tools with your language models
- 💾 **Vector Storage**: Built-in support for vector storage and similarity search
- 🧠 **Memory Management**: Store and retrieve text with associated embeddings
- 🔄 **Async Support**: Built with asyncio for efficient async/await operations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ronmenator/Echo-Py.git
cd Echo-Py
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.py` file with your API credentials:

```python
AZURE_OPENAI_API_KEY = "your-azure-openai-api-key"
AZURE_OPENAI_API_BASE = "your-azure-openai-endpoint"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_TEXT_MODEL = "your-deployment-name"
AZURE_OPENAI_EMBEDDING_MODEL = "your-embedding-deployment-name"

# Optional: For Qdrant vector storage
QDRANT_URL = "your-qdrant-url"
QDRANT_COLLECTION_NAME = "your-collection-name"
QDRANT_API_KEY = "your-qdrant-api-key"
```

## Basic Usage

Here's a simple example of how to use EchoKernel:

```python
import asyncio
from echo_kernel import EchoKernel, AzureOpenAITextProvider, AzureOpenAIEmbeddingProvider
from config import *

async def main():
    # Initialize providers
    text_provider = AzureOpenAITextProvider(
        api_key=AZURE_OPENAI_API_KEY,
        api_base=AZURE_OPENAI_API_BASE,
        api_version=AZURE_OPENAI_API_VERSION,
        model=AZURE_OPENAI_TEXT_MODEL
    )
    
    # Create and configure the kernel
    kernel = EchoKernel()
    kernel.register_provider(text_provider)
    
    # Generate text
    result = await kernel.generate_text("Tell me a joke about programming")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### 1. Tool Integration

You can create and register custom tools:

```python
from echo_kernel.Tool import EchoTool

@EchoTool(description="A custom tool that does something")
def my_custom_tool(param1: str, param2: int) -> str:
    """Tool documentation"""
    # Tool implementation
    return f"Processed {param1} with {param2}"

# Register the tool
kernel.register_tool(my_custom_tool)
```

### 2. Code Interpreter Tool

EchoKernel comes with a built-in code interpreter tool that allows you to execute Python code in a sandboxed environment:

```python
from tools.CodeInterpreterTool import execute_python_code

# Register the code interpreter tool
kernel.register_tool(execute_python_code)

# Use the tool through text generation
result = await kernel.generate_text(
    "Using the code interpreter tool, write a python script that prints 'Hello, World!'"
)
print(result)
```

The code interpreter tool:
- Executes Python code in a sandboxed environment
- Has resource limits for safety
- Returns execution results including stdout and stderr
- Indicates success/failure of code execution

### 3. Vector Memory

Set up vector memory for semantic search capabilities:

```python
from echo_kernel import VectorMemoryProvider, QdrantStorageProvider

# Initialize providers
embedding_provider = AzureOpenAIEmbeddingProvider(
    api_key=AZURE_OPENAI_API_KEY,
    api_base=AZURE_OPENAI_API_BASE,
    api_version=AZURE_OPENAI_API_VERSION,
    model=AZURE_OPENAI_EMBEDDING_MODEL
)

storage_provider = QdrantStorageProvider(
    url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION_NAME,
    api_key=QDRANT_API_KEY
)

memory_provider = VectorMemoryProvider(embedding_provider, storage_provider)

# Register with kernel
kernel.register_provider(embedding_provider)
kernel.register_provider(memory_provider)

# Use memory
await memory_provider.add_text("Important information to remember", {"source": "docs"})
similar_texts = await memory_provider.search_similar("What information do we have?")
```

## Available Providers

### Text Providers
- `AzureOpenAITextProvider`: For Azure OpenAI API
- `OpenAITextProvider`: For OpenAI API

### Embedding Providers
- `AzureOpenAIEmbeddingProvider`: For Azure OpenAI embeddings
- `OpenAIEmbeddingProvider`: For OpenAI embeddings

### Storage Providers
- `QdrantStorageProvider`: For Qdrant vector database
- `InMemoryStorageProvider`: For in-memory vector storage (default)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here] 