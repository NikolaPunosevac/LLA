import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from LLMclassEdditor import LLM

# Allow importing generate_tutorial from sibling directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_tutorial import generate_tutorial, generate_tutorial_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load JSON spec for use in LLM system prompt
_SPEC_PATH = Path(__file__).resolve().parent.parent.parent / "doc" / "docuwise_interview_json_spec.md"
_JSON_SPEC = _SPEC_PATH.read_text(encoding="utf-8") if _SPEC_PATH.exists() else ""

SYSTEM_PROMPT = f"""Si strokovnjak za DocuWise intervjuje. Na podlagi vsebine Word predloge (.docx), ki vsebuje Jinja tage ({{ {{ }}}}, {{% %}}), generiraj JSON po spodnji specifikaciji.

PRAVILA:
- Vrni SAMO veljaven JSON (brez markdown ograj, brez razlage).
- variable_name mora točno ustrezati imenom spremenljivk v predlogi.
- value v options mora ustrezati vrednostim v pogojih predloge.
- Atribute pri object/list moraš eksplicitno navesti.
- show_if pogoji se lahko nanašajo samo na spremenljivke PRED trenutnim vprašanjem.
- Ne mešaj AND in OR v istem pogoju.
- Uporabi show_if ALI hide_if, ne obojega.

SPECIFIKACIJA:
{_JSON_SPEC}
"""


def _extract_json(text: str) -> str:
    """Extract JSON from LLM response, stripping markdown fences if present."""
    # Try to find ```json ... ``` block
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Otherwise assume the whole text is JSON
    return text.strip()


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

    # LLM will be initialized per message based on whether document is provided
    # Store document markdown per connection
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
                    # Extract document markdown if provided
                    document_markdown = data.get("documentMarkdown")
                    
                    # Initialize LLM with document editing prompt if document is provided
                    if document_markdown:
                        logger.info(f"Received document markdown ({len(document_markdown)} chars), using document editing mode")
                        llm = LLM(use_document_editing_prompt=True)
                        # Add document context to the user message
                        user_message_with_doc = f"""Tukaj je vsebina dokumenta v markdown formatu:

{document_markdown}

---

Odvetnik zahteva:
{user_message}"""
                    else:
                        llm = LLM()
                        user_message_with_doc = user_message
                    
                    logger.info(f"Processing chat message: {user_message}")
                    
                    # Send response start signal
                    start_response = {
                        "type": "response_start",
                        "message": ""
                    }
                    await websocket.send(json.dumps(start_response))
                    logger.info("Sent response_start signal")
                    
                    # Collect all streamed chunks into a string
                    full_response = ""
                    
                    # Get LLM response with streaming
                    llm_response = llm.respond(user_message_with_doc, stream=True)
                    for chunk in llm_response:
                        print(chunk)
                        # Accumulate chunks for parsing
                        full_response += chunk
                        
                        # Send chunk to frontend for display
                        chunk_response = {
                            "type": "response_chunk",
                            "message": chunk
                        }
                        await websocket.send(json.dumps(chunk_response))
                        # Small delay to allow frontend to process each chunk in real-time
                        # This prevents all chunks from arriving at once
                        await asyncio.sleep(0.001)  # 1ms delay - imperceptible but allows processing
                        logger.debug(f"Sent response chunk: {chunk}")
                    
                    # Parse for edit commands in format %$[start-end]['text']%$ or %$[start-end]["text"]%$
                    # Pattern matches: %$[number-number]['text']%$ or %$[number-number]["text"]%$
                    # Handle both single and double quotes, with multiline support
                    # Use non-greedy match to capture everything until ']%$ or "]%$
                    edit_pattern_single = r'%\$\[(\d+)-(\d+)\]\[\'(.*?)\'\]%\$'
                    edit_pattern_double = r'%\$\[(\d+)-(\d+)\]\[\"(.*?)\"\]%\$'
                    
                    edit_matches = []
                    # Find matches with single quotes (with DOTALL to handle newlines)
                    for match in re.finditer(edit_pattern_single, full_response, re.DOTALL):
                        edit_matches.append((match.group(1), match.group(2), match.group(3)))
                    # Find matches with double quotes (with DOTALL to handle newlines)
                    for match in re.finditer(edit_pattern_double, full_response, re.DOTALL):
                        edit_matches.append((match.group(1), match.group(2), match.group(3)))
                    
                    if edit_matches:
                        logger.info(f"Found {len(edit_matches)} edit command(s) in response")
                        # Send each edit command as a separate message
                        for start_line, end_line, replacement_text in edit_matches:
                            logger.info(f"Sending edit command: lines {start_line}-{end_line}, text length: {len(replacement_text)}")
                            edit_chunk_response = {
                                "type": "edit_word",
                                "message": replacement_text,
                                "start_line": int(start_line),
                                "end_line": int(end_line)
                            }
                            await websocket.send(json.dumps(edit_chunk_response))
                            await asyncio.sleep(0.001)
                    
                    # Send response end signal
                    end_response = {
                        "type": "response_end",
                        "message": ""
                    }
                    await websocket.send(json.dumps(end_response))
                    logger.info("Sent response_end signal")
                    
                elif data["type"] == "process_docx":
                    # Full pipeline: DOCX text -> LLM -> JSON -> tutorial steps
                    docx_text = data["message"]
                    logger.info("Processing process_docx request")

                    await websocket.send(json.dumps({
                        "type": "status",
                        "message": "Generiram JSON s pomočjo LLM ..."
                    }))

                    # 1. Use LLM to generate interview JSON from DOCX content
                    docx_llm = LLM()
                    docx_llm.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    try:
                        llm_raw = docx_llm.respond(
                            f"Tukaj je vsebina Word predloge:\n\n{docx_text}",
                            stream=False
                        )
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "process_error",
                            "message": f"Napaka pri klicu LLM: {e}"
                        }))
                        logger.error(f"LLM call failed: {e}")
                        continue

                    # 2. Parse JSON from LLM response
                    try:
                        cleaned = _extract_json(llm_raw)
                        interview_data = json.loads(cleaned)
                    except (json.JSONDecodeError, ValueError) as e:
                        await websocket.send(json.dumps({
                            "type": "process_error",
                            "message": f"LLM ni vrnil veljavnega JSON: {e}\n\nOdgovor LLM:\n{llm_raw[:2000]}"
                        }))
                        logger.error(f"JSON parse failed: {e}")
                        continue

                    await websocket.send(json.dumps({
                        "type": "status",
                        "message": "Generiram tutorial ..."
                    }))

                    # 3. Generate tutorial steps
                    try:
                        steps = generate_tutorial(interview_data)
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "process_error",
                            "message": f"Napaka pri generiranju tutoriala: {e}"
                        }))
                        logger.error(f"Tutorial generation failed: {e}")
                        continue

                    # 4. Split steps into slides (by ## sections)
                    slides = []
                    current_slide = []
                    for line in steps:
                        if line.startswith("## ") and current_slide:
                            slides.append("\n".join(current_slide))
                            current_slide = [line]
                        else:
                            current_slide.append(line)
                    if current_slide:
                        slides.append("\n".join(current_slide))

                    # 5. Send result
                    await websocket.send(json.dumps({
                        "type": "tutorial_slides",
                        "message": json.dumps(interview_data),
                        "slides": slides
                    }))
                    logger.info(f"Sent {len(slides)} tutorial slides")

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
