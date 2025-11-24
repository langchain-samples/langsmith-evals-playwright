# LangChain Playwright Evaluator

A LangChain evaluation pipeline that uses Playwright to interact with chat.langchain.com, scrape responses, and evaluate them using LLM-as-judge evaluator.

## Overview

This project demonstrates how to evaluate a web-based LLM application by:
1. Using Playwright to automate interactions with chat.langchain.com
2. Scraping the responses from the web interface
3. Evaluating the scraped responses using LangChain's LLM-as-judge evaluator
4. Using an extensible response format that can be adapted for genUI or browser-based evaluations

## Installation

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)

### Setup

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

4. **Configure environment variables**:
   
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` with your actual API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   ```

## Usage

### Running Evaluations

Run the evaluation script:

```bash
python run_eval.py
```

This will:
- Create a dataset with sample prompts and expected outputs
- Use Playwright to scrape responses from chat.langchain.com
- Evaluate the responses using LLM-as-judge
- Display results and a link to view detailed results in LangSmith

## Architecture

The project consists of:

- **`response_format.py`**: Extensible Pydantic models for structured responses
- **`playwright_scraper.py`**: Playwright automation to interact with chat.langchain.com (runs in headless mode by default)
- **`run_eval.py`**: Main evaluation script that orchestrates the evaluation pipeline

## Response Format

The response format is designed to be extensible for different evaluation scenarios:
- `BaseResponse`: Base class with common fields (text, metadata, timestamp, source)
- `ChatLangchainResponse`: Specific implementation for chat.langchain.com
- Can be extended for genUI or browser-based evaluations

**Note**: The `ChatLangchainResponse` includes a `message_count` field that tracks the number of messages in the conversation. This is currently set to 1 for single-turn evaluations, but is included to support future multi-turn evaluation scenarios where you may want to track conversation length across multiple interactions.

## Limitations

**Note**: The Playwright scraper relies on specific HTML selectors and page structure from chat.langchain.com. If the frontend of chat.langchain.com changes (e.g., updated UI, changed element selectors, or modified page structure), the scraper may break and will need to be updated. The selectors used are based on Playwright's codegen tool, but they may need adjustment if the website is updated.

