
from faster_whisper import WhisperModel
import speech_recognition as sr
import time

print("Loading Whisper base model...")
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)
print("Whisper model loaded!")

recognizer = sr.Recognizer()

try:
    with sr.Microphone() as source:
        print("\nAdjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Speak a sentence now...")
        audio = recognizer.listen(
            source,
            timeout=10,
            phrase_time_limit=10
        )

    # Convert microphone audio to a WAV file in memory.
    import io
    import wave
    import numpy as np

    samples = np.frombuffer(
        audio.get_raw_data(
            convert_rate=16000,
            convert_width=2
        ),
        dtype=np.int16
    )

    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(samples.tobytes())

    wav_buffer.seek(0)

    print("Transcribing locally...")
    start = time.time()

    segments, info = model.transcribe(
        wav_buffer,
        language="en",
        beam_size=1,
        vad_filter=True
    )

    text = " ".join(segment.text.strip() for segment in segments)

    print("\nYou said:", text or "[No speech detected]")
    print(f"Transcription time: {time.time() - start:.2f} seconds")
    print("This transcription used the local Whisper model.")

except Exception as error:
    print(f"\nSTT test failed: {type(error).__name__}: {error}")
