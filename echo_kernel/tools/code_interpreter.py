"""
Code Interpreter - Sandboxed Python Code Execution

This module provides a safe environment for executing Python code with resource limits
and safety measures. It's designed to prevent malicious code execution while allowing
legitimate code to run for educational and development purposes.

The CodeInterpreter class:
- Creates isolated temporary directories for code execution
- Sets resource limits (CPU, memory, file size, open files)
- Implements timeouts to prevent infinite loops
- Cleans up resources automatically
- Works cross-platform (Windows, Linux, macOS)

Safety Features:
- CPU time limit: 30 seconds
- Memory limit: 512MB
- File size limit: 1MB
- Maximum open files: 10
- Process timeout: 30 seconds
- Automatic cleanup of temporary files

Example:
    ```python
    interpreter = CodeInterpreter()
    stdout, stderr = interpreter.execute_code("print('Hello, World!')")
    print(f"Output: {stdout}")
    if stderr:
        print(f"Errors: {stderr}")
    ```
"""

import subprocess
import os
import tempfile
import signal
from typing import Optional, Tuple
import sys
import platform

class CodeInterpreter:
    """
    A sandboxed Python code interpreter with resource limits and safety measures.
    
    This class provides a safe environment for executing Python code by:
    - Creating isolated temporary directories
    - Setting resource limits on the execution process
    - Implementing timeouts to prevent infinite loops
    - Cleaning up resources automatically
    
    The interpreter is designed to be safe for educational and development
    purposes, but should not be used to execute untrusted code in production.
    
    Attributes:
        temp_dir: Path to the temporary directory used for code execution
    """
    
    def __init__(self):
        """Initialize a new CodeInterpreter instance."""
        self.temp_dir = None
        self._setup_temp_dir()

    def _setup_temp_dir(self):
        """
        Set up a temporary directory for code execution.
        
        Creates a unique temporary directory that will be used to store
        and execute Python code. The directory is automatically cleaned up
        when the interpreter is destroyed.
        """
        self.temp_dir = tempfile.mkdtemp(prefix='code_sandbox_')

    def _set_resource_limits(self):
        """
        Set resource limits for the sandbox.
        
        This method sets various resource limits on the current process
        to prevent abuse and ensure safe code execution. Limits include:
        - CPU time limit (30 seconds)
        - Memory limit (512MB)
        - File size limit (1MB)
        - Maximum number of open files (10)
        
        Note:
            Resource limits are only set on Unix-like systems (Linux, macOS).
            On Windows, this method does nothing as the resource module
            is not available.
        """
        if platform.system() != 'Windows':
            try:
                import resource
                # Set CPU time limit (30 seconds)
                resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
                # Set memory limit (512MB)
                resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
                # Set file size limit (1MB)
                resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
                # Set maximum number of open files
                resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))
            except ImportError:
                # Resource module not available, skip setting limits
                pass

    def execute_code(self, code: str) -> Tuple[str, Optional[str]]:
        """Execute Python code in a sandboxed environment.
        
        This method executes the provided Python code in an isolated environment
        with resource limits and safety measures. The code is written to a
        temporary file and executed as a separate process.
        
        Args:
            code: Python code to execute as a string.
        
        Returns:
            A tuple containing (stdout, stderr) where:
            - stdout: The standard output from code execution
            - stderr: The standard error from code execution (None if no errors)
        
        Safety Features:
            - Code is executed in a separate process
            - Resource limits are applied (CPU, memory, file size)
            - Process timeout of 30 seconds
            - Automatic cleanup of temporary files
            - Isolated temporary directory
        
        Example:
            interpreter = CodeInterpreter()
            stdout, stderr = interpreter.execute_code("x = 10; y = 20; print(f'Sum: {x + y}')")
            print(f"Output: {stdout}")  # Output: Sum: 30
        
        Note:
            This method is designed for educational and development purposes.
            Do not use it to execute untrusted code in production environments.
        """
        # Create a temporary file for the code
        script_path = os.path.join(self.temp_dir, 'script.py')
        with open(script_path, 'w') as f:
            f.write(code)

        try:
            # Set up the process with resource limits
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self._set_resource_limits if platform.system() != 'Windows' else None,
                cwd=self.temp_dir
            )

            # Set a timeout of 30 seconds
            try:
                stdout, stderr = process.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                return "", "Execution timed out after 30 seconds"

            # Check if the process was killed due to resource limits
            if process.returncode == -9:  # SIGKILL
                return "", "Process killed due to resource limits exceeded"

            return stdout, stderr if stderr else None

        except Exception as e:
            return "", f"Error executing code: {str(e)}"
        finally:
            # Clean up the temporary file
            try:
                os.remove(script_path)
            except:
                pass

    def __del__(self):
        """
        Cleanup when the interpreter is destroyed.
        
        This method ensures that the temporary directory and all its contents
        are properly cleaned up when the CodeInterpreter instance is destroyed.
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except:
                pass 