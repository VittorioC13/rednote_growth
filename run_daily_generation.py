# Standalone script for Windows Task Scheduler
# This runs once and exits - perfect for scheduled tasks
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rednote_content_generator import RedNoteContentGenerator

def main():
    """Run daily RedNote content generation once"""
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("[ERROR] DEEPSEEK_API_KEY not found in .env file")
        return 1

    try:
        generator = RedNoteContentGenerator(api_key)
        generator.run_daily_generation()
        return 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

if __name__ == "__main__":
    exit(main())
