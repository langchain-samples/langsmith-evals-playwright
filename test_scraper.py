"""
Simple test script for the Playwright scraper.

Run this to test a single scrape operation without running the full evaluation.
"""

import asyncio
from playwright_scraper import scrape_chat_langchain


async def test_scraper():
    """Test the scraper with a single prompt."""
    prompt = "What is LangChain?"
    
    print(f"Testing scraper with prompt: '{prompt}'")
    print("This may take a moment...\n")
    
    # Test with headless=False so you can see what's happening
    response = await scrape_chat_langchain(
        prompt=prompt,
        headless=False,  # Set to True to run in background
        timeout=30000
    )
    
    print("=" * 50)
    print("Response received:")
    print("=" * 50)
    print(f"Text: {response.text}")
    print(f"\nSource: {response.source}")
    print(f"Message count: {response.message_count}")
    print(f"Timestamp: {response.timestamp}")
    print(f"\nMetadata: {response.metadata}")
    if response.raw_html:
        print(f"\nRaw HTML length: {len(response.raw_html)} characters")


if __name__ == "__main__":
    asyncio.run(test_scraper())

