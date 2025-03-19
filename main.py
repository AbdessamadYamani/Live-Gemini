import asyncio
import json
import os
import websockets
from google import genai
import base64
import threading
import http.server
import socketserver
import pathlib
import webbrowser
import time

# Function to start the HTTP server in a separate thread
def start_http_server(port=8000, directory='.'):
    handler = http.server.SimpleHTTPRequestHandler
    # Change to the specified directory
    os.chdir(directory)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"HTTP server running at http://localhost:{port}")
        httpd.serve_forever()

async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
    """Handles the interaction with Gemini API within a websocket session.

    Args:
        client_websocket: The websocket connection to the client.
    """
    try:
        config_message = await client_websocket.recv()
        config_data = json.loads(config_message)
        config = config_data.get("setup", {})
        config["system_instruction"] = """You are a helpful assistant for screen sharing sessions. Your role is to: 
                                        1) Analyze and describe the content being shared on screen 
                                        2) Answer questions about the shared content 
                                        3) Provide relevant information and context about what's being shown 
                                        4) Assist with technical issues related to screen sharing 
                                        5) Maintain a professional and helpful tone. Focus on being concise and clear in your responses."""     

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print("Connected to Gemini API")

            async def send_to_gemini():
                """Sends messages from the client websocket to the Gemini API."""
                try:
                  async for message in client_websocket:
                      try:
                          data = json.loads(message)
                          if "realtime_input" in data:
                              for chunk in data["realtime_input"]["media_chunks"]:
                                  if chunk["mime_type"] == "audio/pcm":
                                      await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
                                      
                                  elif chunk["mime_type"] == "image/jpeg":
                                      await session.send({"mime_type": "image/jpeg", "data": chunk["data"]})
                                      
                      except Exception as e:
                          print(f"Error sending to Gemini: {e}")
                  print("Client connection closed (send)")
                except Exception as e:
                     print(f"Error sending to Gemini: {e}")
                finally:
                   print("send_to_gemini closed")

            async def receive_from_gemini():
                """Receives responses from the Gemini API and forwards them to the client, looping until turn is complete."""
                try:
                    while True:
                        try:
                            print("receiving from gemini")
                            async for response in session.receive():
                                if response.server_content is None:
                                    print(f'Unhandled server message! - {response}')
                                    continue

                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        if hasattr(part, 'text') and part.text is not None:
                                            await client_websocket.send(json.dumps({"text": part.text}))
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                            print("audio mime_type:", part.inline_data.mime_type)
                                            base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                            await client_websocket.send(json.dumps({
                                                "audio": base64_audio,
                                            }))
                                            print("audio received")

                                if response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                        except websockets.exceptions.ConnectionClosedOK:
                            print("Client connection closed normally (receive)")
                            break  # Exit the loop if the connection is closed
                        except Exception as e:
                            print(f"Error receiving from Gemini: {e}")
                            break 

                except Exception as e:
                      print(f"Error receiving from Gemini: {e}")
                finally:
                      print("Gemini connection closed (receive)")

            # Start send loop
            send_task = asyncio.create_task(send_to_gemini())
            # Launch receive loop as a background task
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)

    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        print("Gemini session closed.")

async def main() -> None:
    print("=" * 50)
    print("  Gemini Live Demo Launcher")
    print("=" * 50)
    
    # Prompt for Google API key with regular input (visible typing)
    print("Enter your Google API key below (typing will be visible):")
    api_key = input("> ")
    
    if not api_key.strip():
        print("Error: API key is required to continue.")
        return
    
    # Set API key and initialize client
    os.environ['GOOGLE_API_KEY'] = api_key
    global client, MODEL
    MODEL = "gemini-2.0-flash-exp"
    client = genai.Client(
        http_options={
            'api_version': 'v1alpha',
        }
    )
    
    print("\nInitializing servers...")
    
    # Start HTTP server in a separate thread
    http_port = 8000
    http_server_thread = threading.Thread(
        target=start_http_server,
        args=(http_port, pathlib.Path(__file__).parent),
        daemon=True
    )
    http_server_thread.start()
    print(f"HTTP server started on port {http_port}")
    
    # Give the HTTP server a moment to start
    time.sleep(1)
    
    # Open browser
    url = f"http://localhost:{http_port}"
    print(f"Opening browser at {url}")
    webbrowser.open(url)
    
    # Start WebSocket server
    ws_port = 9083
    print(f"Starting WebSocket server on port {ws_port}...")
    async with websockets.serve(gemini_session_handler, "localhost", ws_port):
        print(f"WebSocket server running on ws://localhost:{ws_port}")
        print("\nPress Ctrl+C to stop the servers")
        await asyncio.Future()  # Keep the server running indefinitely

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServers stopped by user")