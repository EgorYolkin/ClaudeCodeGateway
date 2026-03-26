from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Anthropic-compatible Schemas

class MessageContent(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: str = "text"
    text: Optional[str] = None

class Message(BaseModel):
    model_config = ConfigDict(extra="allow")
    role: str
    content: Union[str, List[Dict[str, Any]], List[MessageContent]]

class AnthropicMessagesRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    model: str
    system: Optional[Any] = None
    messages: List[Message]
    max_tokens: Optional[int] = 4096
    stream: Optional[bool] = False
    stop_sequences: Optional[List[str]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None

class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

class AnthropicMessagesResponse(BaseModel):
    id: str
    type: str = "message"
    role: str = "assistant"
    model: str
    content: List[MessageContent]
    stop_reason: Optional[str] = "end_turn"
    stop_sequence: Optional[str] = None
    usage: Usage

class CountTokensRequest(BaseModel):
    model: str
    system: Optional[str] = None
    messages: List[Message]

class CountTokensResponse(BaseModel):
    input_tokens: int
