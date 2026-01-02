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


async def generate_audio_with_retry(client, formatted_prompt, max_retries=3, delay=10):
    """Generate TTS audio with retry logic for handling API disconnects."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"TTS Generation attempt {attempt + 1}/{max_retries}")
            
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
            
            # Extract audio data
            data = response.candidates[0].content.parts[0].inline_data.data
            print(f"TTS Generation succeeded on attempt {attempt + 1}")
            return data
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Check if it's a retryable error
            if any(x in error_str for x in ['503', 'disconnect', 'overload', 'timeout', 'server']):
                print(f"TTS attempt {attempt + 1} failed (retryable): {e}")
                if attempt < max_retries - 1:
                    wait_time = delay * (attempt + 1)  # Exponential backoff
                    print(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
            else:
                # Non-retryable error
                print(f"TTS generation failed (non-retryable): {e}")
                raise e
    
    # All retries exhausted
    print(f"TTS generation failed after {max_retries} attempts")
    raise last_error


async def after_agent_callback(callback_context: CallbackContext):
    """Generate podcast audio from dialogue after agent completes."""
    await asyncio.sleep(30) 
    
    try:
        client = genai.Client()

        global count
        count += 1

        # Get the podcast content from session state
        podcast_key = f"podcast_content_{count}"
        prompt = callback_context.session.state.get(podcast_key)
        
        if not prompt:
            print(f"No podcast content found for key: {podcast_key}")
            return None
        
        if not isinstance(prompt, dict) or 'dialogue' not in prompt:
            print(f"Invalid podcast content format for key: {podcast_key}")
            return None

        # Format the dialogue for TTS
        formatted_prompt = ""
        for turn in prompt['dialogue']:
            formatted_prompt += f"{turn['speaker']}: {turn['text']}\n"

        print(f"Generating TTS for podcast {count}...")

        # Generate audio with retry logic
        data = await generate_audio_with_retry(client, formatted_prompt)

        # Create podcasts directory if it doesn't exist
        podcast_dir = Path(r"C:\Users\DELL\OneDrive\Desktop\Project\Hackathons\Acharya\podcasts")
        podcast_dir.mkdir(parents=True, exist_ok=True)  
        
        # Save the audio file
        file_name = f"out_{count}.wav"
        wav_file_path = podcast_dir / file_name
        wave_file(str(wav_file_path), data)
        
        print(f"Podcast audio saved to {wav_file_path}")

    except Exception as e:
        print(f"Error generating podcast audio: {e}")

    return None