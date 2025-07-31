#!/usr/bin/env python3
"""
Test script to verify the CSE downloader setup
"""

import os
import sys
from cse_downloader import CSEDownloader

def test_setup():
    """Test if all dependencies are properly installed"""
    print("Testing CSE Downloader setup...")
    
    try:
        # Test imports
        import selenium
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ Selenium and WebDriver Manager imported successfully")
        
        # Test download directory creation
        downloader = CSEDownloader("test_downloads")
        print("✓ CSEDownloader initialized successfully")
        
        # Check if downloads directory was created
        if os.path.exists("test_downloads"):
            print("✓ Download directory created successfully")
            # Clean up test directory
            os.rmdir("test_downloads")
        else:
            print("✗ Download directory not created")
            return False
            
        print("\n🎉 All tests passed! The setup is ready.")
        print("\nTo run the actual downloader:")
        print("python cse_downloader.py")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nPlease install required packages:")
        print("pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"✗ Setup error: {e}")
        return False

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
