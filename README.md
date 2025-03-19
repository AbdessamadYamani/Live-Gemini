Gemini Live Demo - Screen Share Assistant
This project demonstrates a real-time screen sharing and voice interaction application using Google's Gemini API. Users can share their screen and interact verbally with the Gemini model, which provides both text and audio responses based on the screen content.
Features

Real-time screen sharing analysis with Gemini AI
Voice input and output support
Simple web interface with Material Design styling
Single command to start both servers (WebSocket and HTTP)
Automatic browser opening for convenience

Prerequisites

Python 3.8 or higher
A Google API key for Gemini (obtain from Google AI Studio)
A compatible web browser (Chrome recommended)

Installation
1. Clone the Repository and go to its path
2. Create and Activate Virtual Environment
For Windows:
bashCopypython -m venv .venv
.venv\Scripts\activate
For macOS/Linux:
bashCopypython -m venv .venv
source .venv/bin/activate
3. Install Dependencies
bashCopypip install -r requirements.txt
Project Structure
Copygemini-live-demo/
├── main.py                # Main Python script with both servers
├── index.html             # Web interface 
├── PCMP.js                # Audio processor for client-side playback
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
Running the Application

From the project directory with your virtual environment activated, run:

bashCopypython main.py

When prompted, enter your Google API key.
A browser window will automatically open to http://localhost:8000
Grant permission for screen sharing when prompted by your browser.
Click the microphone button to start voice interaction.

Usage Instructions

Start Screen Sharing: When the browser opens, select the window or tab you want to share.
Start Voice Input: Click the microphone button (green circular button) to begin sending voice data.
Interact with Gemini: Speak naturally to ask questions about what's on your screen.
Stop Voice Input: Click the microphone-off button to stop sending audio.
Stop the Application: Press Ctrl+C in the terminal to shut down the servers.

Troubleshooting

Connection Errors: Make sure your Google API key is correct and has access to the Gemini API.
Audio Not Working: Check your browser's microphone permissions.
Screen Sharing Issues: Ensure you've granted the proper permissions in your browser.

Technical Details
The application consists of:

A Python-based WebSocket server that communicates with Google's Gemini API
An HTTP server to serve the web interface
A browser-based client handling screen capture and audio I/O
Audio processing for real-time voice interaction