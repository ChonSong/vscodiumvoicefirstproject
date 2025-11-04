"""
ADK IDE Implementation

A comprehensive AI-powered Integrated Development Environment built on Google's Agent Development Kit (ADK).
This system provides a high-density coding agent environment with multi-agent architecture, 
secure code execution, and intelligent development assistance.
"""

__version__ = "1.0.0"
__author__ = "ADK IDE Team"
__description__ = "AI-Powered IDE using Google Agent Development Kit"

# Core imports for easy access
from .agents import *
from .services import *
from .config import *

__all__ = [
    "__version__",
    "__author__", 
    "__description__"
]