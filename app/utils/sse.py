import json
from typing import Any, Dict

def format_sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """Formats a message as an Anthropic-compatible SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

def message_start_event(model: str, message_id: str) -> str:
    return format_sse_event("message_start", {
        "type": "message_start",
        "message": {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }
    })

def content_block_start_event(index: int = 0) -> str:
    return format_sse_event("content_block_start", {
        "type": "content_block_start",
        "index": index,
        "content_block": {"type": "text", "text": ""}
    })

def content_block_delta_event(text: str, index: int = 0) -> str:
    return format_sse_event("content_block_delta", {
        "type": "content_block_delta",
        "index": index,
        "delta": {"type": "text_delta", "text": text}
    })

def content_block_stop_event(index: int = 0) -> str:
    return format_sse_event("content_block_stop", {
        "type": "content_block_stop",
        "index": index
    })

def message_delta_event(stop_reason: str = "end_turn", output_tokens: int = 0) -> str:
    return format_sse_event("message_delta", {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason, "stop_sequence": None},
        "usage": {"output_tokens": output_tokens}
    })

def message_stop_event() -> str:
    return format_sse_event("message_stop", {"type": "message_stop"})

def ping_event() -> str:
    return format_sse_event("ping", {"type": "ping"})
