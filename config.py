import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "")
AZURE_OPENAI_TEXT_MODEL = os.getenv("AZURE_OPENAI_TEXT_MODEL", "")
AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "")

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# Agent Logging Configuration
# Set to False to disable print statements in agents
AGENT_LOGGING_ENABLED = os.getenv("AGENT_LOGGING_ENABLED", "True").lower() == "true" 