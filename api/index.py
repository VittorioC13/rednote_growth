"""
Vercel serverless function entry point
Serverless-compatible - no file I/O
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the serverless Flask app
from web_interface_vercel import app
