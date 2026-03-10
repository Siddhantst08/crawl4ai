#!/usr/bin/env python3
"""
Test script for the event crawler.

This script provides basic testing functionality to verify the crawler works
before running it on the full Excel file.
"""

import asyncio
import pandas as pd
import json
import os
from event_crawler import EventCrawler
from advanced_event_crawler import AdvancedEventCrawler

def create_test_excel():
    """Create a test Excel file with sample websites."""
    test_data = [
        {
            'Website': 'https://example.com/events',
            'Extraction_Instructions': 'Look for event listings in the main content area',
            'Additional_Info': 'Test website for events'
        },
        {
            'Website': 'https://demo.wp-events-plugin.com/',
            'Extraction_Instructions': 'Extract events from WordPress event plugin',
            'Additional_Info': 'WordPress events demo site'
        }
    ]
    
    df = pd.DataFrame(test_data)
    test_file = 'test_websites.xlsx'
    df.to_excel(test_file, index=False)
    print(f"Created test Excel file: {test_file}")
    return test_file

async def test_basic_crawler():
    """Test the basic event crawler."""
    print("Testing basic event crawler...")
    
    # Create test Excel file
    test_file = create_test_excel()
    
    try:
        # Initialize crawler
        crawler = EventCrawler(test_file)
        
        # Load and display Excel data
        df = crawler.load_excel_data()
        print(f"Loaded {len(df)} websites from test file")
        
        # Test crawling a single website
        if len(df) > 0:
            first_url = df.iloc[0]['Website']
            print(f"Testing crawl of: {first_url}")
            
            # Test single website crawl
            result = await crawler.crawl_website(
                first_url, 
                df.iloc[0].get('Extraction_Instructions', ''),
                df.iloc[0].get('Additional_Info', '')
            )
            
            print(f"Crawl result: {result['success']}")
            print(f"Events found: {len(result.get('events', []))}")
            
        print("Basic crawler test completed!")
        
    except Exception as e:
        print(f"Error in basic crawler test: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)

async def test_advanced_crawler():
    """Test the advanced event crawler."""
    print("Testing advanced event crawler...")
    
    # Create test Excel file
    test_file = create_test_excel()
    
    try:
        # Initialize advanced crawler
        crawler = AdvancedEventCrawler(test_file)
        
        # Load and display Excel data
        df = pd.read_excel(test_file)
        print(f"Loaded {len(df)} websites from test file")
        
        # Test website type detection
        if len(df) > 0:
            first_url = df.iloc[0]['Website']
            print(f"Testing website type detection for: {first_url}")
            
            # Test with a mock HTML content
            mock_html = """
            <html>
            <body>
                <div class="wp-block-post">
                    <h2>Test Event</h2>
                    <div class="event-date">2024-01-15</div>
                    <div class="event-location">Online</div>
                </div>
            </body>
            </html>
            """
            
            website_type = crawler.detect_website_type(first_url, mock_html)
            print(f"Detected website type: {website_type}")
            
        print("Advanced crawler test completed!")
        
    except Exception as e:
        print(f"Error in advanced crawler test: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)

def test_extraction_schema():
    """Test the extraction schema creation."""
    print("Testing extraction schema creation...")
    
    # Test basic crawler schema
    crawler = EventCrawler("dummy.xlsx")
    schema = crawler.create_extraction_schema()
    
    print("Basic crawler schema:")
    print(json.dumps(schema, indent=2))
    
    # Test advanced crawler schema
    advanced_crawler = AdvancedEventCrawler("dummy.xlsx")
    schema = advanced_crawler.create_extraction_strategy("generic")
    
    print("Advanced crawler schema:")
    print("Schema created successfully")
    
    print("Schema test completed!")

async def main():
    """Main test function."""
    print("Starting event crawler tests...\n")
    
    # Test schema creation
    test_extraction_schema()
    print()
    
    # Test basic crawler
    await test_basic_crawler()
    print()
    
    # Test advanced crawler
    await test_advanced_crawler()
    print()
    
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())