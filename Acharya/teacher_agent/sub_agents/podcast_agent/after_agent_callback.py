import asyncio
from google import genai
from google.genai import types
import wave
from google.adk.agents.callback_context import CallbackContext
from pathlib import Path

count = 0

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

async def after_agent_callback(callback_context: CallbackContext):
    await asyncio.sleep(60)
    client = genai.Client()

    global count
    count += 1

    prompt = callback_context.session.state[f"podcast_content_{count}"]

    formatted_prompt = ""
    for turn in prompt['dialogue']:
        formatted_prompt += f"{turn['speaker']}: {turn['text']}\n"

    response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=formatted_prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                types.SpeakerVoiceConfig(
                    speaker='Alice',
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore',
                        )
                    )
                ),
                types.SpeakerVoiceConfig(
                    speaker='Bob',
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Puck',
                        )
                    )
                ),
                ]
            )
        )
    )
    )

    data = response.candidates[0].content.parts[0].inline_data.data

    podcast_dir = Path(r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\podcasts")
    podcast_dir.mkdir(parents=True, exist_ok=True)  
    
    file_name = f"out_{count}.wav"
    wav_file_path = podcast_dir / file_name
    wave_file(str(wav_file_path), data)  # Convert Path to string

    return None