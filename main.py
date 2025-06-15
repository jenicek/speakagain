import os
import requests
from supabase import create_client, Client
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://speak-again-v2.lovable.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/")
def index():
    return {"message": "Hello World"}


@app.post("/tts")
def tts(text: str, user_id: str, gender: str):
    """
    Text-to-Speech endpoint.
    :param text: The text to convert to speech.
    :return: An MP3 file containing the speech.
    """
    response = supabase.table("user_voices").select("*").filter("user_id", "eq", user_id).execute()
    voice_id = response.data[0]['elevenlabs_voice_id']
    if voice_id is None:
        if gender == "m":
            voice_id = "tzHEU0BULePYMOTlJocD"
        else:
            voice_id = "Xb7hH8MSUJpSbSDYk0k2"

    resp = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"Xi-Api-Key": ELEVENLABS_API_KEY},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
        }
    )
    raw = resp.content

    return Response(content=raw, media_type="audio/mpeg",
                    headers={"Content-Disposition": "attachment; filename=output.mp3"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5544)
