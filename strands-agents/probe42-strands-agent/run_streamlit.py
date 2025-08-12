#!/usr/bin/env python3
"""Run the Streamlit app."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit application."""
    app_path = Path(__file__).parent / "src" / "probe_agent" / "streamlit_app.py"
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_path),
        "--server.port", "8501",
        "--server.address", "localhost"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()