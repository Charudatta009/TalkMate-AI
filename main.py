import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ai_services import process_audio, generate_ai_response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
@app.get("/")
def home():
    return {"status": "OK"}


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
           
            audio_data = await websocket.receive_bytes()
            
            # Process audio → text
            user_text = process_audio(audio_data)
            
            # Get AI response
            ai_response = generate_ai_response(user_text)
            
            # Send back response
            await websocket.send_json({
                "text": ai_response["text"],
                "audio": ai_response["audio"],
                "corrections": ai_response["corrections"]
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
