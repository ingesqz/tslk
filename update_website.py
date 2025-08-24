#!/usr/bin/env python3
"""
Script to regenerate the TSLK website after updating the data.
"""

import subprocess
import os
import sys

def main():
    """Regenerate the website."""
    print("🔄 Regenerating TSLK website...")
    
    # Check if www folder exists
    if not os.path.exists("www"):
        print("❌ www folder not found!")
        return
    
    # Change to www directory
    os.chdir("www")
    
    try:
        # Run the website generation script
        result = subprocess.run([sys.executable, "generate_website.py"], 
                              capture_output=True, text=True, check=True)
        
        print("✅ Website regenerated successfully!")
        print(result.stdout)
        
        print("\n📁 Files created:")
        print("  - www/index.html (main website)")
        print("  - www/logo.png (TSLK logo)")
        print("  - www/README.md (documentation)")
        
        print("\n🌐 To view the website:")
        print("  - Open www/index.html in your web browser")
        print("  - Or run: open www/index.html")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating website: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 