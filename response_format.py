"""
Extensible response format models for different evaluation scenarios.

This module provides base classes and specific implementations for
scraping responses from different sources (chat.langchain.com, genUI, browser, etc.).
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response class with common fields for all response types."""
    
    text: str = Field(description="The main text content of the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was captured")
    source: str = Field(description="The source of the response (e.g., 'chat.langchain.com', 'genUI', 'browser')")
    
    def to_eval_format(self) -> Dict[str, Any]:
        """Convert response to format expected by evaluators."""
        return {
            "messages": [{"role": "ai", "content": self.text}]
        }
    
    def extract_text(self) -> str:
        """Extract the text content for evaluation."""
        return self.text


class ChatLangchainResponse(BaseResponse):
    """Response format specifically for chat.langchain.com."""
    
    source: str = Field(default="chat.langchain.com", description="Source identifier")
    raw_html: Optional[str] = Field(default=None, description="Raw HTML of the response element")
    message_count: int = Field(default=1, description="Number of messages in the response")


# Placeholder classes for future extensibility
class GenUIResponse(BaseResponse):
    """Response format for genUI evaluations (to be implemented)."""
    source: str = Field(default="genUI", description="Source identifier")
    # Add genUI-specific fields as needed


class BrowserResponse(BaseResponse):
    """Response format for browser-based evaluations (to be implemented)."""
    source: str = Field(default="browser", description="Source identifier")
    interaction_log: Optional[list] = Field(default=None, description="Log of browser interactions")
    # Add browser-specific fields as needed


def normalize_response(response: BaseResponse) -> str:
    """Normalize any response type to a string for evaluation."""
    return response.extract_text()

