import asyncio
import json
import logging
import sys
from pathlib import Path
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from LLMclass import LLM

# Allow importing generate_tutorial from sibling directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_tutorial import generate_tutorial_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_llm_response(question: str) -> str:
    """
    LLM service function - placeholder for your desired model or API service.
    
    Args:
        question: The user's question/message
        
    Returns:
        The LLM's response as a string
    """
    # TODO: Replace this with your actual LLM service implementation
    # Example implementations:
    # - OpenAI API: openai.ChatCompletion.create(...)
    # - Anthropic API: anthropic.Anthropic().messages.create(...)
    # - Local model: your_model.generate(...)
    # - HuggingFace: pipeline(...)
    
    # Placeholder response
    return f"LLM Response to: {question}"


async def handle_client(websocket, path):
    """
    Handle incoming websocket connections and messages.
    
    Args:
        websocket: The websocket connection
        path: The connection path (should be '/ws')
    """
    client_address = websocket.remote_address
    logger.info(f"Client connected from {client_address} on path {path}")
    
    # Only accept connections to /ws path
    if path != "/ws":
        logger.warning(f"Rejecting connection to invalid path: {path}")
        await websocket.close(code=1008, reason="Invalid path")
        return

    llm = LLM()
    # Store document markdown per connection (not yet used in LLM calls)
    document_markdown = None
    
    try:
        async for message in websocket:
            try:
                # Parse the incoming message
                data = json.loads(message)
                logger.info(f"Received message: {data}")
                
                # Validate message format
                if not isinstance(data, dict) or "type" not in data or "message" not in data:
                    logger.warning(f"Invalid message format: {data}")
                    continue
                
                # Handle chat messages
                if data["type"] == "chat":
                    user_message = data["message"]
                    # Extract document markdown if provided (not yet used in LLM calls)
                    document_markdown = data.get("documentMarkdown")
                    if document_markdown:
                        logger.info(f"Received document markdown ({len(document_markdown)} chars), stored but not yet used in LLM calls")
                    logger.info(f"Processing chat message: {user_message}")
                    
                    # Send response start signal
                    start_response = {
                        "type": "response_start",
                        "message": ""
                    }
                    await websocket.send(json.dumps(start_response))
                    logger.info("Sent response_start signal")
                    
                    # Get LLM response with streaming
                    llm_response = llm.respond(user_message, stream=True)
                    for chunk in llm_response:
                        print(chunk)
                        chunk_response = {
                            "type": "response_chunk",
                            "message": chunk
                        }
                        await websocket.send(json.dumps(chunk_response))
                        # Small delay to allow frontend to process each chunk in real-time
                        # This prevents all chunks from arriving at once
                        await asyncio.sleep(0.001)  # 1ms delay - imperceptible but allows processing
                        logger.debug(f"Sent response chunk: {chunk}")
                    
                    # Send response end signal
                    end_response = {
                        "type": "response_end",
                        "message": ""
                    }
                    await websocket.send(json.dumps(end_response))
                    logger.info("Sent response_end signal")
                    
                elif data["type"] == "generate_tutorial":
                    # Generate a step-by-step tutorial from interview JSON
                    raw = data["message"]
                    logger.info("Processing generate_tutorial request")

                    try:
                        interview_data = json.loads(raw) if isinstance(raw, str) else raw
                        tutorial_md = generate_tutorial_text(interview_data)
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        error_response = {
                            "type": "tutorial_error",
                            "message": f"Napaka pri obdelavi JSON: {e}"
                        }
                        await websocket.send(json.dumps(error_response))
                        logger.error(f"Tutorial generation failed: {e}")
                        continue

                    # Stream the tutorial using the same protocol as chat
                    await websocket.send(json.dumps({
                        "type": "response_start",
                        "message": ""
                    }))

                    # Send in line-sized chunks for a streaming feel
                    for line in tutorial_md.split("\n"):
                        chunk_response = {
                            "type": "response_chunk",
                            "message": line + "\n"
                        }
                        await websocket.send(json.dumps(chunk_response))
                        await asyncio.sleep(0.001)

                    await websocket.send(json.dumps({
                        "type": "response_end",
                        "message": ""
                    }))
                    logger.info("Tutorial sent successfully")

                else:
                    logger.warning(f"Unknown message type: {data['type']}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except ConnectionClosed:
        logger.info(f"Client {client_address} disconnected")
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")


async def main():
    """
    Start the websocket server on localhost:8000
    """
    host = "localhost"
    port = 8000
    
    logger.info(f"Starting websocket server on ws://{host}:{port}/ws")
    
    async with serve(handle_client, host, port):
        logger.info(f"Websocket server is running on ws://{host}:{port}/ws")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
