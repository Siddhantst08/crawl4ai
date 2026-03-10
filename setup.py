#!/usr/bin/env python3
"""
Setup script for the Event Website Crawler.

This script helps users quickly set up and configure the crawler.
"""

import os
import sys
import subprocess
import argparse

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_sample_excel():
    """Create a sample Excel file for testing."""
    try:
        import pandas as pd
        
        sample_data = [
            {
                'Website': 'https://example.com/events',
                'Extraction_Instructions': 'Extract event information from the main content area',
                'Additional_Info': 'Sample website for testing'
            },
            {
                'Website': 'https://demo.wp-events-plugin.com/',
                'Extraction_Instructions': 'Extract events from WordPress event plugin',
                'Additional_Info': 'WordPress events demo site'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_excel('sample_input.xlsx', index=False)
        print("✓ Created sample_input.xlsx")
        return True
        
    except ImportError:
        print("✗ pandas not available, skipping sample file creation")
        return False
    except Exception as e:
        print(f"✗ Failed to create sample file: {e}")
        return False

def verify_crawl4ai():
    """Verify Crawl4AI is properly installed."""
    try:
        import crawl4ai
        print(f"✓ Crawl4AI version: {crawl4ai.__version__}")
        return True
    except ImportError:
        print("✗ Crawl4AI not found. Please install it manually.")
        return False

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='Setup Event Website Crawler')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies')
    parser.add_argument('--create-sample', action='store_true', help='Create sample Excel file')
    parser.add_argument('--verify', action='store_true', help='Verify installation')
    
    args = parser.parse_args()
    
    print("Event Website Crawler Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Create sample file if requested
    if args.create_sample:
        create_sample_excel()
    
    # Verify installation
    if args.verify or not any([args.install_deps, args.create_sample]):
        verify_crawl4ai()
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Prepare your Excel file with website URLs")
    print("2. Run: python event_crawler.py --excel your_file.xlsx")
    print("3. Or run: python advanced_event_crawler.py --excel your_file.xlsx")

if __name__ == "__main__":
    main()