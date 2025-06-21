import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ai_services import process_audio, generate_ai_response
from dotenv import load_dotenv
import uvicorn
import json

load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive data from client
            data = await websocket.receive()
            
            if 'text' in data:
                # Handle text messages (like conversation start)
                message = json.loads(data['text'])
                if message.get('action') == 'start_conversation':
                    response = generate_ai_response("", message.get('mode', 'casual'))
                    await websocket.send_text(json.dumps(response))
            
            elif 'bytes' in data:
                # Handle audio data
                audio_bytes = data['bytes']
                user_text = process_audio(audio_bytes)
                ai_response = generate_ai_response(user_text)
                await websocket.send_text(json.dumps(ai_response))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close(code=1011)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
