import asyncio
import json
import logging
from websockets.server import serve
from websockets.exceptions import ConnectionClosed

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
                    logger.info(f"Processing chat message: {user_message}")
                    
                    # Get LLM response
                    #llm_response = await get_llm_response(user_message)
                    llm_response = "This is a test response"                    
                    
                    # Send response back to client
                    response = {
                        "type": "response",
                        "message": llm_response
                    }
                    await websocket.send(json.dumps(response))
                    logger.info(f"Sent response: {response}")
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
