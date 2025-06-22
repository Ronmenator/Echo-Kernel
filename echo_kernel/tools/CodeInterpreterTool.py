"""
Code Interpreter Tool for EchoKernel

This module provides a safe code execution tool that can be used by AI models
to run Python code in a sandboxed environment. The tool includes resource limits
and safety measures to prevent malicious code execution.

The code interpreter:
- Executes Python code in an isolated environment
- Sets resource limits (CPU, memory, file size)
- Implements timeouts to prevent infinite loops
- Cleans up temporary files automatically
- Returns both stdout and stderr from execution

Example:
    ```python
    from tools.CodeInterpreterTool import execute_python_code
    
    # Register with kernel
    kernel.register_tool(execute_python_code)
    
    # AI can now use the tool to execute code
    result = await kernel.generate_text(
        "Write and execute code to calculate fibonacci numbers"
    )
    ```
"""

from typing import Dict, Any, List
from echo_kernel.EchoTool import EchoTool
from .code_interpreter import CodeInterpreter

interpreter = CodeInterpreter()

def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Executes Python code in a sandboxed environment.
    :param code: The Python code to execute.
    :return: A dictionary containing the result of the execution.
    """
    return interpreter.execute_code(code)

def code_interpreter_tools() -> List[EchoTool]:
    """
    Returns a list of code interpreter tools.
    :return: A list of code interpreter tools.
    """
    return [
        EchoTool(
            name="execute_python_code",
            description="Executes Python code in a sandboxed environment.",
            func=execute_python_code,
        )
    ] 