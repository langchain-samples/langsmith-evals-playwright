# LangChain Playwright Evaluator

A LangChain evaluation pipeline that uses Playwright to interact with chat.langchain.com, scrape responses, and evaluate them using LLM-as-judge evaluator.

## Overview

This example demonstrates how to evaluate a web-based LLM application by automating browser interactions with Playwright, scraping responses from chat.langchain.com, and evaluating them using LangChain's LLM-as-judge evaluator. It provides an extensible response format that can be adapted for genUI or browser-based evaluations, making it useful for testing and validating web-based LLM applications that don't expose direct APIs.

## Quickstart

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

2. **Install Playwright browsers**:
   ```bash
   uv run playwright install
   ```

3. **Configure environment variables**:
   
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` with your actual API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   LANGCHAIN_API_KEY=your_langchain_api_key_here
   ```

### Running the Example

Run the evaluation script:

```bash
uv run python run_eval.py
```

This will:
- Create a dataset with sample prompts and expected outputs
- Use Playwright to scrape responses from chat.langchain.com
- Evaluate the responses using LLM-as-judge
- Display results and a link to view detailed results in LangSmith

**Note**: In the LangSmith UI, you may need to manually add the evaluator column (e.g., "correctness") to the results table. Look for the column customization options in the LangSmith interface to display evaluator feedback.

To test the scraper alone in headful mode with a single prompt: `uv run python test_scraper.py`

## Configuration

### Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key for the LLM-as-judge evaluator
- `LANGCHAIN_API_KEY` (required): Your LangChain API key for LangSmith integration

### Optional Parameters

The Playwright scraper accepts optional parameters:
- `headless` (default: `True`): Whether to run the browser in headless mode
- `timeout` (default: `30000`): Maximum time to wait for response in milliseconds

## Additional Notes


### Architecture

The project consists of:
- **`response_format.py`**: Extensible Pydantic models for structured responses
- **`playwright_scraper.py`**: Playwright automation to interact with chat.langchain.com (runs in headless mode by default)
- **`run_eval.py`**: Main evaluation script that orchestrates the evaluation pipeline

### Limitations

The Playwright scraper relies on specific HTML selectors and page structure from chat.langchain.com. If the frontend of chat.langchain.com changes (e.g., updated UI, changed element selectors, or modified page structure), the scraper may break and will need to be updated. The selectors used are based on Playwright's codegen tool, but they may need adjustment if the website is updated.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
