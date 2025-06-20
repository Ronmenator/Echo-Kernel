#!/usr/bin/env python3
"""
Command-line interface for EchoKernel.
"""

import asyncio
import argparse
import sys
import os
from typing import Optional

from .EchoKernel import EchoKernel
from .providers.AzureOpenAITextProvider import AzureOpenAITextProvider
from .providers.OpenAITextProvider import OpenAITextProvider


def load_config() -> dict:
    """Load configuration from environment variables."""
    return {
        "azure_openai_api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "azure_openai_api_base": os.getenv("AZURE_OPENAI_API_BASE"),
        "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        "azure_openai_text_model": os.getenv("AZURE_OPENAI_TEXT_MODEL"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
    }


async def interactive_mode(kernel: EchoKernel):
    """Run EchoKernel in interactive mode."""
    print("EchoKernel Interactive Mode")
    print("Type 'quit' or 'exit' to exit")
    print("Type 'help' for available commands")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("EchoKernel> ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("  - Type any text to generate a response")
                print("  - 'quit' or 'exit': Exit the program")
                print("  - 'help': Show this help message")
                continue
            elif not user_input:
                continue
            
            print("Generating response...")
            response = await kernel.generate_text(user_input)
            print(f"Response: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def single_query(kernel: EchoKernel, query: str):
    """Run a single query and exit."""
    try:
        response = await kernel.generate_text(query)
        print(response)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="EchoKernel - AI-powered application framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  echo-kernel --interactive                    # Start interactive mode
  echo-kernel "Tell me a joke"                 # Single query
  echo-kernel --provider openai "Hello world"  # Use OpenAI provider
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Single query to process (if not provided, runs in interactive mode)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--provider",
        choices=["azure", "openai"],
        default="azure",
        help="AI provider to use (default: azure)"
    )
    
    parser.add_argument(
        "--model",
        help="Model to use (overrides default for the provider)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if args.provider == "azure":
        if not config["azure_openai_api_key"]:
            print("Error: AZURE_OPENAI_API_KEY environment variable is required", file=sys.stderr)
            sys.exit(1)
        if not config["azure_openai_api_base"]:
            print("Error: AZURE_OPENAI_API_BASE environment variable is required", file=sys.stderr)
            sys.exit(1)
        if not config["azure_openai_text_model"]:
            print("Error: AZURE_OPENAI_TEXT_MODEL environment variable is required", file=sys.stderr)
            sys.exit(1)
    elif args.provider == "openai":
        if not config["openai_api_key"]:
            print("Error: OPENAI_API_KEY environment variable is required", file=sys.stderr)
            sys.exit(1)
    
    async def run():
        # Initialize kernel
        kernel = EchoKernel()
        
        # Set up provider
        if args.provider == "azure":
            text_provider = AzureOpenAITextProvider(
                api_key=config["azure_openai_api_key"],
                api_base=config["azure_openai_api_base"],
                api_version=config["azure_openai_api_version"],
                model=args.model or config["azure_openai_text_model"]
            )
        else:  # openai
            text_provider = OpenAITextProvider(
                api_key=config["openai_api_key"],
                model=args.model or config["openai_model"]
            )
        
        kernel.register_provider(text_provider)
        
        # Run in appropriate mode
        if args.query:
            await single_query(kernel, args.query)
        else:
            await interactive_mode(kernel)
    
    # Run the async function
    asyncio.run(run())


if __name__ == "__main__":
    main() 