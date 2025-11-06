"""Streaming route for agent responses."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from oc_commands_analyzer_agent.src.core.agent import get_oc_analyzer_agent
from oc_commands_analyzer_agent.src.settings import settings
from oc_commands_analyzer_agent.utils.pylogger import get_python_logger

logger = get_python_logger(settings.PYTHON_LOG_LEVEL)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str
    thread_id: str = "default"


async def stream_agent_response(
    message: str, thread_id: str
) -> AsyncGenerator[str, None]:
    """Stream agent response as Server-Sent Events.

    Args:
        message: User message to process
        thread_id: Thread ID for conversation history

    Yields:
        Server-Sent Event formatted strings
    """
    try:
        async with get_oc_analyzer_agent(enable_checkpointing=settings.USE_CHECKPOINTING) as agent:
            logger.info(f"Processing message for thread_id: {thread_id}")

            # Prepare config with thread_id
            config = {"configurable": {"thread_id": thread_id}}

            # Use values mode to get complete snapshots
            event_count = 0
            async for event in agent.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="values",
            ):
                event_count += 1
                logger.info(f"Received event {event_count}: {type(event)}")

                # event is the full state with messages
                if isinstance(event, dict) and "messages" in event:
                    messages = event["messages"]

                    # Get the last message
                    if len(messages) > 0:
                        last_msg = messages[-1]

                        # Log what we got
                        logger.info(f"Last message type: {type(last_msg).__name__}, has content: {hasattr(last_msg, 'content')}")

                        # Stream AI messages
                        if hasattr(last_msg, "content") and last_msg.content:
                            msg_type = getattr(last_msg, "type", "unknown")

                            # Only stream if it's from AI or a tool
                            if msg_type in ["ai", "AIMessage", "tool"]:
                                data = {
                                    "type": "message",
                                    "content": last_msg.content,
                                    "role": msg_type,
                                }
                                yield f"data: {json.dumps(data)}\n\n"

                        # Handle tool calls
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            for tool_call in last_msg.tool_calls:
                                tool_data = {
                                    "type": "tool_call",
                                    "name": tool_call.get("name", "unknown"),
                                    "args": tool_call.get("args", {}),
                                }
                                logger.info(f"Tool call: {tool_call.get('name')}")
                                yield f"data: {json.dumps(tool_data)}\n\n"

            # Send done signal
            logger.info(f"Finished streaming response, total events: {event_count}")
            yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Error in stream_agent_response: {e}", exc_info=True)
        error_data = {"type": "error", "content": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat endpoint.

    Args:
        request: Chat request with message and thread_id

    Returns:
        StreamingResponse with Server-Sent Events
    """
    return StreamingResponse(
        stream_agent_response(request.message, request.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
