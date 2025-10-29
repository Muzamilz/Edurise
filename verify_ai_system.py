#!/usr/bin/env python3
"""
Quick AI System Verification
Runs the most important tests to verify AI system is working
"""
import subprocess
import sys

def main():
    """Quick verification of AI system"""
    print("==> EduRise AI System - Quick Verification")
    print("=" * 50)
    
    # Run the complete system test
    try:
        result = subprocess.run(
            ["python", "tests/integration/test_ai_system_complete.py"], 
            capture_output=True, 
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("\nSUCCESS: AI System Verification PASSED!")
            print("==> EduRise AI is fully operational and ready for use!")
        else:
            print("\n❌ AI System Verification: FAILED!")
            print("⚠️  Please check the errors above and run individual tests for debugging.")
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Test file not found. Make sure you're in the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()