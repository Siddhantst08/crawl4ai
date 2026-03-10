#!/usr/bin/env python3

"""
Advanced Event Website Crawler using Crawl4AI
Improved version with:
- Free LLM support (Groq/OpenRouter)
- Multi-strategy fallback
- JS rendering
- Cleaned LLM input
- Safe JSON parsing
"""

import asyncio
import pandas as pd
from pydantic import BaseModel
import json
import logging
import os
import re
import requests
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from crawl4ai.async_configs import CrawlerRunConfig
from crawl4ai import LLMConfig, CacheMode

from bs4 import BeautifulSoup

# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("advanced_crawler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# -----------------------------
# Pydantic Models
# -----------------------------

class Event(BaseModel):
    event_name: str | None = None
    organizer: str | None = None
    description: str | None = None
    registration_required: str | None = None
    deadline: str | None = None
    registration_cost: str | None = None
    event_venue: str | None = None
    language: str | None = None
    link: str | None = None
    event_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None

class Events(BaseModel):
    events: list[Event]


# -----------------------------
# Main crawler class
# -----------------------------

class AdvancedEventCrawler:

    def __init__(self, excel_file: str):

        self.excel_file = excel_file
        self.crawl_results = []

        # concurrency control
        self.semaphore = asyncio.Semaphore(3)

        # ---------------------
        # FREE LLM CONFIG
        # ---------------------

        self.llm_config = LLMConfig(
        provider="openrouter/meta-llama/llama-3.3-70b-instruct",  # note: usually provider is "<vendor>/<model>"
        api_token=os.getenv("OPENROUTER_API_KEY"),
        # api_token = "",
        temperature=0,
        )

    # -----------------------------
    # URL Validation
    # -----------------------------

    def _is_valid_url(self, url: str):

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    # -----------------------------
    # Safe JSON
    # -----------------------------

    def safe_json(self, data):

        try:
            return json.loads(data)
        except:
            return {"events": []}

    # -----------------------------
    # Clean page text for LLM
    # -----------------------------

    def clean_page_text(self, html):

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        return text[:12000]

    # -----------------------------
    # LLM Prompt
    # -----------------------------

    def llm_prompt(self):

        return """
            You are a strict JSON extraction engine.

            Extract all events from the webpage and return ONLY a single JSON object, no explanations, no code fences, no backticks.

            Use this exact schema:
            {
            "events":[
            {
                "event_name": "",
                "organizer": "",
                "description": "",
                "registration_required": "",
                "deadline": "",
                "registration_cost": "",
                "event_venue": "",
                "language": "",
                "link": "",
                "event_date": "",
                "start_time": "",
                "end_time": ""
            }
            ]
            }

            If a field is unknown, set it to null.
            Output MUST be valid JSON.
            """

    # -----------------------------
    # CSS Extraction Strategy
    # -----------------------------

    def css_strategy(self):

        schema = {
            "type": "object",
            "properties": {
                "events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "event_name": {"type": "string"},
                            "organizer": {"type": "string"},
                            "description": {"type": "string"},
                            "registration_required": {"type": "string"},
                            "deadline": {"type": "string"},
                            "registration_cost": {"type": "string"},
                            "event_venue": {"type": "string"},
                            "language": {"type": "string"},
                            "link": {"type": "string"},
                            "event_date": {"type": "string"},
                            "start_time": {"type": "string"},
                            "end_time": {"type": "string"}
                        }
                    }
                }
            }
        }

        instructions = """
Extract all events listed on the page.
Return structured JSON.
"""

        return JsonCssExtractionStrategy(
            schema=schema,
            instruction=instructions
        )

    # -----------------------------
    # LLM Strategy
    # -----------------------------

    def llm_strategy(self):
        result = LLMExtractionStrategy(
            llm_config=self.llm_config,
            schema=Events.model_json_schema(),  # or Events.schema() depending on version
            extraction_type="schema",          # this flag matters in newer versions
            instruction=self.llm_prompt(),
            verbose=True
        )
        logger.info(result.llm_config)
        return result

    # -----------------------------
    # Crawl with fallback
    # -----------------------------

    async def crawl_with_fallback(self, url, additional_info):

        logger.info(f"Starting crawl: {url}")

        strategies = [

            # ("css_fast", False),
            # ("css_js", True),
            ("llm", False)

        ]

        async with self.semaphore:

            for strategy_name, use_js in strategies:
                try:

                    if strategy_name == "llm":
                        extraction_strategy = self.llm_strategy()
                    else:
                        extraction_strategy = self.css_strategy()

                    async with AsyncWebCrawler(verbose=True) as crawler:
                        logger.warning(f"Trying strategy {strategy_name}")
                        result = await crawler.arun(
                            url=url,
                            config=CrawlerRunConfig(
                            extraction_strategy=extraction_strategy,
                            cache_mode=CacheMode.BYPASS,
                            wait_for=None,
                            page_timeout=120000
                            ),
                            js_execution=use_js,
                        )
                        logger.warning(f"Got result for strategy {strategy_name}: success={result.success}, content_length={len(result.markdown)}, extracted_content={result.extracted_content}")
                        logger.info(result.extracted_content)
                        # logger.info(extraction_strategy)
                    if result.success and result.extracted_content:

                        extracted_data = self.safe_json(result.extracted_content)
                        # logger.info(f"Extracted data for {url}: {extracted_data}")

                        return {
                            "url": url,
                            "additional_info": additional_info,
                            "crawl_timestamp": datetime.now().isoformat(),
                            "success": True,
                            "strategy_used": strategy_name,
                            "events": extracted_data,
                            "raw_content_length": len(result.markdown),
                            "error": None
                        }

                except Exception as e:

                    logger.warning(f"{strategy_name} failed: {e}")

        return {
            "url": url,
            "additional_info": additional_info,
            "crawl_timestamp": datetime.now().isoformat(),
            "success": False,
            "strategy_used": None,
            "events": [],
            "raw_content_length": 0,
            "error": "All strategies failed"
        }

    # -----------------------------
    # Crawl all websites
    # -----------------------------

    async def crawl_all_websites(self, df):

        tasks = []

        for _, row in df.iterrows():

            url = row["Website"]
            info = row.get("Additional_Info", "")

            if pd.notna(url) and self._is_valid_url(url):

                tasks.append(
                    self.crawl_with_fallback(url, info)
                )

        results = await asyncio.gather(*tasks)

        self.crawl_results = results

    # -----------------------------
    # Send Events to Supabase
    # -----------------------------

    def send_to_supabase(self, events_data, endpoint="https://ujzprgiumifdtyaialvu.supabase.co/functions/v1/post-event"):
        """
        Send events data to Supabase via POST request
        
        Args:
            events_data (list): List of event dictionaries to send
            endpoint (str): Supabase endpoint URL
        """
        try:
            # Prepare headers for Supabase
            headers = {
                'Content-Type': 'application/json',
                'apikey': os.getenv('SUPABASE_ANON_KEY', ''),  # Optional: if you have an API key
                'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_KEY", "")}'  # Optional: if you have a service key
            }
            
            # Prepare the payload
            payload = {
                "events": events_data,
                "timestamp": datetime.now().isoformat(),
                "source": "advanced_event_crawler"
            }
            
            logger.info(f"Sending {len(events_data)} events to Supabase at {endpoint}")
            
            # Make the POST request
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Successfully sent {len(events_data)} events to Supabase")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"Failed to send events to Supabase. Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending events to Supabase: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    # -----------------------------
    # Save Results
    # -----------------------------

    def save_results(self):

        if not self.crawl_results:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"event_results_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(self.crawl_results, f, indent=2)

        rows = []

        for result in self.crawl_results:

            for event in result.get("events", []):

                row = {
                    "url": result["url"],
                    "strategy": result.get("strategy_used"),
                    **event
                }

                rows.append(row)

        df = pd.DataFrame(rows)

        df.to_csv(
            f"event_results_{timestamp}.csv",
            index=False
        )

        # Send events to Supabase
        if rows:
            success = self.send_to_supabase(rows)
            if success:
                logger.info("Events successfully sent to Supabase")
            else:
                logger.warning("Failed to send events to Supabase, but local files were saved")
        else:
            logger.info("No events to send to Supabase")

        logger.info("Results saved.")

    # -----------------------------
    # Main run
    # -----------------------------

    async def run(self):

        logger.info("Starting crawler")

        df = pd.read_excel(self.excel_file)

        await self.crawl_all_websites(df)

        self.save_results()

        logger.info("Crawler finished")


# -----------------------------
# CLI
# -----------------------------

def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--excel",
        required=True,
        help="Excel file with Website column"
    )

    args = parser.parse_args()

    if not os.path.exists(args.excel):

        print("Excel file not found")
        return

    crawler = AdvancedEventCrawler(args.excel)

    asyncio.run(crawler.run())


if __name__ == "__main__":

    main()