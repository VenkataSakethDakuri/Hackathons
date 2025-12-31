import asyncio
from google import genai
from google.genai import types
import wave
from google.adk.agents.callback_context import CallbackContext

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

    prompt = callback_context.session.state["podcast_content"]

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

    global count
    count += 1

    file_name = f"out_{count}.wav"
    wav_file_path=rf"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\{file_name}"
    wave_file(wav_file_path, data)

    return None