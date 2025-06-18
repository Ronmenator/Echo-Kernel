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

from typing import Optional, Tuple
from code_interpreter import CodeInterpreter
from echo_kernel.Tool import EchoTool
import json

@EchoTool(description="Execute Python code in a sandboxed environment and return the results")
def execute_python_code(code: str) -> str:
    """
    Execute Python code in a sandboxed environment.
    
    This tool allows AI models to run Python code safely. The code is executed
    in an isolated environment with resource limits to prevent abuse.
    
    Args:
        code: Python code to execute as a string.
    
    Returns:
        JSON string containing execution results with the following structure:
        {
            "success": bool,
            "stdout": str,
            "stderr": str,
            "error": str (if execution failed)
        }
    
    Safety Features:
        - CPU time limit: 30 seconds
        - Memory limit: 512MB
        - File size limit: 1MB
        - Maximum open files: 10
        - Automatic cleanup of temporary files
    
    Example:
        ```python
        result = execute_python_code("print('Hello, World!')\nx = 2 + 2\nprint(f'2 + 2 = {x}')")
        # Returns: {"success": true, "stdout": "Hello, World!\\n2 + 2 = 4\\n", "stderr": null}
        ```
    
    Note:
        This tool is designed for educational and development purposes.
        Do not use it to execute untrusted code in production environments.
    """
    try:
        # Create code interpreter instance
        interpreter = CodeInterpreter()
        
        # Execute the code
        stdout, stderr = interpreter.execute_code(code)
        
        # Determine if execution was successful
        success = stderr is None or stderr.strip() == ""
        
        # Prepare result
        result = {
            "success": success,
            "stdout": stdout,
            "stderr": stderr
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Handle any errors in the execution process
        error_result = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": str(e)
        }
        return json.dumps(error_result, indent=2) 