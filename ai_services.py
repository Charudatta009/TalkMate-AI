import os
import openai
from elevenlabs.client import ElevenLabs  # Updated import
from dotenv import load_dotenv
import tempfile

load_dotenv()

# Configure APIs
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))  # New client initialization

def process_audio(audio_bytes):
    """Convert speech to text using Whisper"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.seek(0)
            transcript = openai.Audio.transcribe("whisper-1", tmp)
        return transcript["text"]
    except Exception as e:
        print(f"Audio processing error: {e}")
        return ""

def generate_ai_response(user_input):
    """Generate text response and corrections"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You're an English tutor. Correct grammar naturally and keep responses concise."
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        
        ai_text = response.choices[0].message["content"]
        audio = generate_audio(ai_text)
        corrections = analyze_grammar(user_input)
        
        return {
            "text": ai_text,
            "audio": audio,
            "corrections": corrections
        }
    except Exception as e:
        print(f"AI response error: {e}")
        return {
            "text": "Sorry, I encountered an error. Please try again.",
            "audio": b"",
            "corrections": []
        }

def generate_audio(text):
    """Convert text to speech using ElevenLabs"""
    try:
        # Updated ElevenLabs v1.x API call
        audio = elevenlabs_client.generate(
            text=text,
            voice="Rachel",
            model="eleven_monolingual_v2"
        )
        return audio  # Returns bytes directly
    except Exception as e:
        print(f"Audio generation error: {e}")
        return b""

def analyze_grammar(text):
    """Identify grammar mistakes (simplified)"""
    common_mistakes = {
        "goed": ("went", "Incorrect past tense of 'go'"),
        "writed": ("wrote", "Incorrect past tense of 'write'"),
        "eated": ("ate", "Incorrect past tense of 'eat'"),
        "doesn't has": ("doesn't have", "Use 'have' with 'doesn't'")
    }
    
    corrections = []
    for wrong, (correct, explanation) in common_mistakes.items():
        if wrong in text.lower():
            corrections.append({
                "original": wrong,
                "corrected": correct,
                "explanation": explanation
            })
    
    return corrections
