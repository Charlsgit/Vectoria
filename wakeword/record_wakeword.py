import wave
import pyaudio

DEVICE_INDEX = 9
RATE = 48000
CHANNELS = 1
CHUNK = 3840
SECONDS = 3

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=CHUNK
)

print("========================================")
print(" VECTORIA WAKE WORD RECORDER")
print("========================================")
print()
print("Get ready...")
input("Press ENTER, then say 'Hey Vectoria'...")

print("SPEAK NOW!")

frames = []

for _ in range(int(RATE / CHUNK * SECONDS)):
    data = stream.read(
        CHUNK,
        exception_on_overflow=False
    )
    frames.append(data)

print("Recording finished.")

stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(
    "wakeword_test.wav",
    "wb"
) as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))

print()
print("Saved: wakeword_test.wav")