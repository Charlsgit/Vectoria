import pyaudio
import numpy as np
import openwakeword.model as oww

MODEL = "wakeword/training/output/oww_training/hey_vectoria.onnx"

RATE = 16000
CHUNK = 1280

model = oww.Model(wakeword_models=[MODEL])

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("\n=== Vectoria Wake Word Live Test ===")
print("Listening...")
print("Say: Hey Vectoria")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16)

        prediction = model.predict(samples)
        score = list(prediction.values())[0]

        print(f"\rScore: {score:.3f}", end="", flush=True)

        if score >= 0.5:
            print(f"\n\n?? HEY VECTORIA DETECTED! Score: {score:.3f}\n")

except KeyboardInterrupt:
    print("\n\nStopping...")

finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
