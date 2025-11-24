"""
Playwright scraper for interacting with chat.langchain.com.

This module provides functions to automate browser interactions with
chat.langchain.com, submit prompts, and scrape responses.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from response_format import ChatLangchainResponse

# Global configuration
CHAT_LANGCHAIN_URL = "https://chat.langchain.com"


async def scrape_chat_langchain(
    prompt: str,
    headless: bool = True,
    timeout: int = 30000
) -> ChatLangchainResponse:
    """
    Scrape a response from chat.langchain.com for a given prompt.
    
    Args:
        prompt: The prompt/question to submit to chat.langchain.com
        headless: Whether to run the browser in headless mode
        timeout: Maximum time to wait for response (milliseconds)
    
    Returns:
        ChatLangchainResponse: Structured response containing the scraped text
    
    Raises:
        Exception: If scraping fails or times out
    """
    browser: Optional[Browser] = None
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=headless)
            # Grant clipboard permissions so we can read and write to clipboard
            context = await browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = await context.new_page()
            
            # Navigate to chat.langchain.com
            await page.goto(CHAT_LANGCHAIN_URL, wait_until="networkidle")
            
            # Find and click the input field using the role selector (from codegen)
            textbox = page.get_by_role("textbox", name="Ask me anything about")
            await textbox.click()
            
            # Fill in the prompt
            await textbox.fill(prompt)
            
            # Submit by pressing Enter
            await textbox.press("Enter")
            
            # Wait for response to appear and complete streaming
            # Wait for the response to start appearing
            await asyncio.sleep(2)
            
            # Wait for streaming to complete - look for the copy button as an indicator
            # that the response is ready
            copy_button = page.get_by_role("button", name="Copy", exact=True)
            # Wait for copy button to appear (indicates response has started)
            await copy_button.wait_for(state="visible", timeout=timeout)
            
            # Wait for network to be idle (indicates streaming is complete)
            try:
                await page.wait_for_load_state("networkidle", timeout=timeout)
            except PlaywrightTimeoutError:
                # If networkidle times out, wait a bit more as fallback
                await asyncio.sleep(2)
            
            # Clear the clipboard first to avoid stale content
            await page.evaluate("async () => await navigator.clipboard.writeText('')")
            
            # Click the copy button to copy the response to clipboard
            await copy_button.click()
            
            # Wait briefly for clipboard to be updated
            await page.wait_for_timeout(300)  # 300ms wait for clipboard
            
            # Extract the response text from clipboard
            response_text = await page.evaluate("async () => await navigator.clipboard.readText()")
            
            # Verify we got actual content (not empty or stale clipboard)
            if not response_text:
                # Fallback: try to get text from the page if clipboard failed
                response_text = await page.evaluate("""
                    () => {
                        // Try to find the response text near the copy button
                        const copyButton = Array.from(document.querySelectorAll('button')).find(
                            btn => btn.textContent?.trim() === 'Copy'
                        );
                        if (copyButton) {
                            // Look for text in the same container or nearby
                            let container = copyButton.closest('[class*="message"], [class*="response"], [class*="assistant"]');
                            if (!container) {
                                container = copyButton.parentElement?.parentElement;
                            }
                            if (container) {
                                const text = container.innerText || container.textContent;
                                return text.replace(/Copy/g, '').trim();
                            }
                        }
                        return null;
                    }
                """)
            
            # Get raw HTML if we can find the response element
            raw_html = None
            try:
                # Try to find the response element
                response_elements = await page.query_selector_all('[class*="message"], [class*="response"], [class*="assistant"]')
                if response_elements:
                    raw_html = await response_elements[-1].inner_html()
            except Exception:
                pass
            
            # Count messages (not currently used but useful for multi-turn evaluations)
            message_count = len(await page.query_selector_all('[class*="message"]'))
            if message_count == 0:
                message_count = 1  # Fallback: we know we got a response
            
            return ChatLangchainResponse(
                text=response_text.strip(),
                raw_html=raw_html,
                message_count=message_count,
                metadata={
                    "url": page.url,
                    "headless": headless,
                    "timeout": timeout,
                }
            )
            
    except Exception as e:
        return ChatLangchainResponse(
            text=f"Error scraping chat.langchain.com: {str(e)}",
            metadata={"error": str(e), "error_type": type(e).__name__}
        )
    finally:
        if browser:
            await browser.close()

