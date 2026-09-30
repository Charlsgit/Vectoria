import pyaudio
import wave

RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1280
RECORD_SECONDS = 5

OUTPUT = "live_test.wav"

audio = pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Recording for 5 seconds...")
print("Say: Hey Vectoria")

frames = []

for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

print("Recording finished.")

stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(OUTPUT, "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))

print(f"Saved: {OUTPUT}")