#!/usr/bin/env python3

"""
Test script to demonstrate the Supabase POST request functionality
"""

import json
import requests
from datetime import datetime
import os

def test_supabase_post():
    """Test the Supabase POST request functionality"""
    
    # Sample event data (similar to what the crawler would generate)
    sample_events = [
        {
            "url": "https://example.com/event1",
            "strategy": "llm",
            "event_name": "Tech Conference 2024",
            "organizer": "Tech Corp",
            "description": "Annual technology conference featuring industry leaders",
            "registration_required": "Yes",
            "deadline": "2024-12-01",
            "registration_cost": "$500",
            "event_venue": "Convention Center",
            "language": "English",
            "link": "https://example.com/event1",
            "event_date": "2024-12-15",
            "start_time": "09:00",
            "end_time": "17:00"
        },
        {
            "url": "https://example.com/event2", 
            "strategy": "llm",
            "event_name": "Webinar: AI Trends",
            "organizer": "AI Institute",
            "description": "Online webinar about the latest AI trends and developments",
            "registration_required": "Yes",
            "deadline": "2024-11-30",
            "registration_cost": "Free",
            "event_venue": "Online",
            "language": "English",
            "link": "https://example.com/webinar",
            "event_date": "2024-12-05",
            "start_time": "14:00",
            "end_time": "15:30"
        }
    ]
    
    # Your Supabase endpoint
    endpoint = "https://abc.supabase.co/post"
    
    # Prepare headers for Supabase
    headers = {
        'Content-Type': 'application/json',
        'apikey': os.getenv('SUPABASE_ANON_KEY', ''),  # Optional: if you have an API key
        'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_KEY", "")}'  # Optional: if you have a service key
    }
    
    # Prepare the payload
    payload = {
        "events": sample_events,
        "timestamp": datetime.now().isoformat(),
        "source": "advanced_event_crawler_test"
    }
    
    print(f"Sending {len(sample_events)} events to Supabase at {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Make the POST request
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Successfully sent events to Supabase!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to send events to Supabase")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending events to Supabase: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_supabase_post()