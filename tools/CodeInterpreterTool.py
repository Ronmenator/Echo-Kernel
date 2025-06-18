from typing import Optional, Tuple
from code_interpreter import CodeInterpreter
from echo_kernel.Tool import EchoTool
import json

@EchoTool(description="Execute Python code in a sandboxed environment with resource limits")
def execute_python_code(code: str) -> str:
    """Execute Python code in a sandboxed environment.
    
    Args:
        code (str): The Python code to execute
        
    Returns:
        str: JSON string containing the execution results
    """
    interpreter = CodeInterpreter()
    try:
        stdout, stderr = interpreter.execute_code(code)
        result = {
            "stdout": stdout,
            "stderr": stderr if stderr else None,
            "success": stderr is None
        }
        return json.dumps(result)
    finally:
        del interpreter 