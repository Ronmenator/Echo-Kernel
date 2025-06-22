"""
Tools package for EchoKernel

This package contains various tools that can be used with EchoKernel,
including web access tools, code interpreter tools, and other utilities.
"""

from .web_access import WebAccess
from .WebAccessTool import get_web_content, search_web
from .CodeInterpreterTool import execute_python_code

__all__ = [
    'WebAccess',
    'get_web_content', 
    'search_web',
    'execute_python_code'
] 