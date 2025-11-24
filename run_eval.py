"""
Main evaluation script for LangChain Playwright Evaluator.

This script follows the evaluation pattern from the multi_agent.ipynb notebook:
1. Creates a dataset with sample prompts and expected outputs
2. Defines an async application function that uses Playwright to scrape responses
3. Sets up LLM-as-judge evaluators using openevals
4. Runs the evaluation using LangSmith client
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langsmith import Client
from openevals.llm import create_async_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from playwright_scraper import scrape_chat_langchain
from response_format import ChatLangchainResponse

# Load environment variables
load_dotenv()

# Initialize model (inline, no utils/ directory)
model = init_chat_model("openai:gpt-4o-mini")  # Using a cost-effective model for evaluation

# Initialize LangSmith client
client = Client()


async def run_app(inputs: dict) -> dict:
    """
    Application logic function that runs the Playwright scraper.
    
    This function is called by the evaluator for each test case.
    It extracts the prompt from inputs, calls the scraper, and returns
    the response in the format expected by evaluators.
    
    Args:
        inputs: Dictionary containing the input data (e.g., {"messages": [...]})
    
    Returns:
        Dictionary with messages in the format expected by evaluators
    """
    # Extract prompt from inputs
    if "messages" in inputs:
        # Handle different message formats
        messages = inputs["messages"]
        if isinstance(messages, list):
            if isinstance(messages[0], dict):
                prompt = messages[0].get("content", "")
            else:
                prompt = str(messages[0])
        else:
            prompt = str(messages)
    elif "question" in inputs:
        prompt = inputs["question"]
    else:
        prompt = str(inputs)
    
    # Scrape response from chat.langchain.com
    response: ChatLangchainResponse = await scrape_chat_langchain(
        prompt=prompt,
        headless=True,
        timeout=30000
    )
    
    # Return in format expected by evaluators
    return {"messages": [{"role": "ai", "content": response.text}]}


async def main():
    """Main function to run the evaluation."""
    
    print("Setting up evaluation...")
    
    # 1. Create dataset
    dataset_name = "LangChain Playwright Evaluator: Chat Langchain Responses"
    
    examples = [
        {
            "question": "What is LangChain?",
            "response": "LangChain is a framework for building applications with LLMs.",
        },
        {
            "question": "How do I create an agent in LangChain?",
            "response": "You can create an agent using LangChain's agent creation tools.",
        },
        {
            "question": "What is LangGraph?",
            "response": "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
        },
        {
            "question": "How do I use tools with LangChain?",
            "response": "You can use tools by binding them to your LLM using the bind_tools method.",
        },
        {
            "question": "What is the difference between LangChain and LangGraph?",
            "response": "LangChain is a framework for building LLM applications, while LangGraph is specifically for building stateful, multi-actor applications.",
        },
    ]
    
    # Check if dataset exists, create if not
    if not client.has_dataset(dataset_name=dataset_name):
        print(f"Creating dataset: {dataset_name}")
        dataset = client.create_dataset(dataset_name=dataset_name)
        client.create_examples(
            inputs=[{"messages": [{"role": "user", "content": ex["question"]}]} for ex in examples],
            outputs=[{"messages": [{"role": "ai", "content": ex["response"]}]} for ex in examples],
            dataset_id=dataset.id
        )
        print(f"Dataset created with {len(examples)} examples")
    else:
        print(f"Dataset '{dataset_name}' already exists")
    
    # 2. Set up evaluators
    print("Setting up evaluators...")
    
    # Use openevals pre-built correctness evaluator
    correctness_evaluator = create_async_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        feedback_key="correctness",
        judge=model
    )
    
    print("Evaluators ready")
    print(f"Using correctness prompt:\n{CORRECTNESS_PROMPT}\n")
    
    # 3. Run evaluation
    print("Running evaluation...")
    print("This may take a while as it scrapes responses from chat.langchain.com...")
    
    experiment_results = await client.aevaluate(
        run_app,
        data=dataset_name,
        evaluators=[correctness_evaluator],
        experiment_prefix="playwright-chat-langchain",
        num_repetitions=1,
        max_concurrency=2  # Limit concurrency to avoid overwhelming the website
    )
    
    print("\n" + "="*50)
    print("Evaluation Complete!")
    print("="*50)
    
    # Print summary
    if hasattr(experiment_results, 'experiment_url'):
        print(f"\nView detailed results at: {experiment_results.experiment_url}")
    elif hasattr(experiment_results, 'experiment_id'):
        print(f"\nExperiment ID: {experiment_results.experiment_id}")
        print(f"View results in LangSmith dashboard")
    
    print("\nEvaluation finished successfully!")


if __name__ == "__main__":
    asyncio.run(main())

