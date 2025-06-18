import subprocess
import os
import tempfile
import signal
from typing import Optional, Tuple
import sys
import platform

class CodeInterpreter:
    def __init__(self):
        self.temp_dir = None
        self._setup_temp_dir()

    def _setup_temp_dir(self):
        """Set up a temporary directory for code execution."""
        self.temp_dir = tempfile.mkdtemp(prefix='code_sandbox_')

    def _set_resource_limits(self):
        """Set resource limits for the sandbox."""
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
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code (str): Python code to execute
            
        Returns:
            Tuple[str, Optional[str]]: (stdout, stderr)
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
        """Cleanup when the interpreter is destroyed."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except:
                pass 