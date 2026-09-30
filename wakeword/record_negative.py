import os
import wave
import pyaudio

OUTPUT_DIR = "wakeword/data/negative"
NUM_RECORDINGS = 30

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16

os.makedirs(OUTPUT_DIR, exist_ok=True)

audio = pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("\n=== Vectoria Negative Sample Recorder ===")
print("We will record 30 negative samples.")
print("DO NOT say: 'Hey Vectoria'")
print("Press ENTER to record each sample.")
print("Press Ctrl+C to stop.\n")

try:
    for i in range(1, NUM_RECORDINGS + 1):

        input(f"Press ENTER for recording {i}/{NUM_RECORDINGS}...")

        print("🎤 Speak normally — NOT 'Hey Vectoria'")

        frames = []

        # Record approximately 2 seconds
        for _ in range(int(SAMPLE_RATE / CHUNK * 2)):
            data = stream.read(
                CHUNK,
                exception_on_overflow=False
            )
            frames.append(data)

        filename = os.path.join(
            OUTPUT_DIR,
            f"negative_{i:03d}.wav"
        )

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(frames))

        print(f"Saved: {filename}\n")

except KeyboardInterrupt:
    print("\nRecording stopped.")

finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()

print("\nDone!")