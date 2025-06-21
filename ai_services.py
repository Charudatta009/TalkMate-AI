import os
import openai
from elevenlabs import generate as elevenlabs_generate
from dotenv import load_dotenv
import tempfile

load_dotenv()

# Configure APIs
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def process_audio(audio_bytes):
    """Convert speech to text using Whisper"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.seek(0)
            transcript = openai.Audio.transcribe("whisper-1", tmp)
        return transcript["text"]
    except Exception as e:
        print(f"Audio processing error: {e}")
        return ""

def generate_ai_response(user_input, mode="casual"):
    """Generate text and audio response"""
    try:
        # Generate text with GPT
        prompt = {
            "casual": "You're an English tutor. Have a friendly conversation",
            "job_interview": "You're a job interviewer. Ask relevant questions",
            "travel": "You're a travel assistant. Help with English for travel"
        }.get(mode, "Have a conversation in English")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        
        ai_text = response.choices[0].message["content"]
        
        # Generate speech with ElevenLabs
        audio = elevenlabs_generate(
            text=ai_text,
            voice="Rachel",
            model="eleven_monolingual_v2",
            api_key=ELEVENLABS_API_KEY
        )
        
        # Simple grammar check (replace with proper NLP in production)
        corrections = []
        if "you was" in user_input.lower():
            corrections.append({
                "original": "you was",
                "corrected": "you were",
                "explanation": "Use 'were' with 'you' in past tense"
            })
        
        return {
            "text": ai_text,
            "audio": audio,  # This will be base64 encoded audio
            "corrections": corrections
        }
        
    except Exception as e:
        print(f"AI generation error: {e}")
        return {
            "text": "Sorry, I encountered an error. Please try again.",
            "audio": None,
            "corrections": []
        }
