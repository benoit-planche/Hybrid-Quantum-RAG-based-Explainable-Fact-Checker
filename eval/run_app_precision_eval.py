#!/usr/bin/env python3
"""
Simple runner script for app.py precision evaluation
"""

import subprocess
import sys
import os

def main():
    """Run the app precision evaluation."""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the evaluation script
    eval_script = os.path.join(script_dir, "evaluate_app_precision.py")
    
    # Check if the evaluation script exists
    if not os.path.exists(eval_script):
        print(f"❌ Evaluation script not found: {eval_script}")
        sys.exit(1)
    
    # Make the script executable
    os.chmod(eval_script, 0o755)
    
    # Run the evaluation with default parameters
    print("🚀 Running app.py precision evaluation...")
    print("This will test the fact-checking accuracy of your Streamlit application")
    print("=" * 60)
    
    try:
        # Run the evaluation script
        result = subprocess.run([
            sys.executable, eval_script,
            "--lambda", "1.0"
        ], cwd=script_dir, check=True)
        
        print("\n🎉 Evaluation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Evaluation failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 