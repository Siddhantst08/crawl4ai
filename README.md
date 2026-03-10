# Event Website Crawler using Crawl4AI

A powerful web crawler built with Crawl4AI to extract event information from multiple websites listed in an Excel file.

## Features

- **Multi-website crawling**: Process multiple websites from an Excel file
- **Smart extraction**: Extract specific event fields using AI-powered extraction
- **Flexible output**: Save results in JSON or CSV format
- **Error handling**: Robust error handling and logging
- **Website detection**: Automatically detect website types for optimized extraction
- **Rate limiting**: Built-in rate limiting to avoid overwhelming servers

## Required Fields

The crawler extracts the following event information:

- `event_name` - Event title/name
- `organizer` - Event organizer
- `description` - Event description
- `registration_required` - Whether registration is needed
- `deadline` - Registration deadline or event date
- `registration_cost` - Cost of registration
- `event_venue` - Physical or virtual location
- `language` - Language of the event
- `link` - URL to event page
- `comments` - Additional relevant information

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Install Crawl4AI (if not already installed):

```bash
pip install crawl4ai
```

## Usage

### Basic Crawler

```bash
python event_crawler.py --excel sample_input.xlsx --output json
```

### Advanced Crawler

```bash
python advanced_event_crawler.py --excel sample_input.xlsx
```

### Testing

```bash
python test_crawler.py
```

## Excel File Format

The Excel file should have the following columns:

| Column Name | Description | Required |
|-------------|-------------|----------|
| Website | URL of the website to crawl | Yes |
| Extraction_Instructions | Custom instructions for extraction | No |
| Additional_Info | Additional metadata about the website | No |

### Example Excel Structure

```
Website                    | Extraction_Instructions                    | Additional_Info
https://example.com/events | Extract events from main content area      | Tech conference site
https://events.org         | Look for workshop listings                 | Monthly workshops
```

## Output Formats

### JSON Output

```json
[
  {
    "url": "https://example.com/events",
    "additional_info": "Tech conference site",
    "crawl_timestamp": "2024-01-15T10:30:00",
    "success": true,
    "events": [
      {
        "event_name": "Tech Conference 2024",
        "organizer": "Tech Org",
        "description": "Annual technology conference",
        "registration_required": "yes",
        "deadline": "2024-01-31",
        "registration_cost": "Free",
        "event_venue": "Convention Center",
        "language": "English",
        "link": "https://example.com/event/tech2024",
        "comments": "Early bird registration available"
      }
    ],
    "raw_content_length": 15000,
    "error": null
  }
]
```

### CSV Output

The CSV format flattens the event data for easy analysis:

| url | event_name | organizer | description | registration_required | deadline | registration_cost | event_venue | language | link | comments | success |
|-----|------------|-----------|-------------|----------------------|----------|-------------------|-------------|----------|------|----------|---------|
| https://example.com/events | Tech Conference 2024 | Tech Org | Annual technology conference | yes | 2024-01-31 | Free | Convention Center | English | https://example.com/event/tech2024 | Early bird registration available | True |

## Configuration

### Basic Crawler Options

- `--excel`: Path to Excel file with website URLs (required)
- `--output`: Output format (json or csv, default: json)

### Advanced Crawler Features

- **Website Type Detection**: Automatically detects WordPress, Eventbrite, and generic sites
- **Multiple Extraction Strategies**: Falls back between JSON-CSS and LLM extraction
- **Enhanced Analysis**: Provides quality metrics for extracted events
- **Detailed Logging**: Comprehensive logging for debugging

## Error Handling

The crawler includes robust error handling for:

- Invalid URLs
- Network timeouts
- Extraction failures
- Malformed JSON responses
- Rate limiting violations

## Logging

Logs are saved to:
- `crawler.log` (basic crawler)
- `advanced_crawler.log` (advanced crawler)

Log levels:
- INFO: General progress and results
- WARNING: Non-critical issues
- ERROR: Critical failures

## Performance Tips

1. **Rate Limiting**: The crawler includes built-in delays to avoid overwhelming servers
2. **Concurrent Processing**: Multiple websites are processed concurrently
3. **Memory Management**: Large responses are handled efficiently
4. **Cache Management**: Uses bypass_cache=True for fresh data

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Network Errors**: Check internet connection and website accessibility
3. **Extraction Failures**: Some websites may require custom extraction strategies
4. **Memory Issues**: For very large websites, consider processing in smaller batches

### Debug Mode

Enable verbose logging by modifying the crawler initialization:

```python
async with AsyncWebCrawler(verbose=True) as crawler:
    # Your crawling code
```

## Examples

### Simple Usage

```python
from event_crawler import EventCrawler

# Initialize crawler
crawler = EventCrawler('websites.xlsx')

# Run crawler
import asyncio
asyncio.run(crawler.run())
```

### Advanced Usage

```python
from advanced_event_crawler import AdvancedEventCrawler

# Initialize advanced crawler
crawler = AdvancedEventCrawler('websites.xlsx')

# Run with detailed analysis
asyncio.run(crawler.run())
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information