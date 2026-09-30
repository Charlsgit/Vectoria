import numpy as np
import wave

from openwakeword.model import Model
from openwakeword.utils import AudioFeatures


MODEL_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\wakeword\training\output\oww_training\hey_vectoria.onnx"

WAV_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\wakeword\training\output\oww_training\hey_vectoria\negative_test\0.wav"

print("Loading model...")
model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

print("Model loaded.")
print()


# Read WAV
with wave.open(WAV_PATH, "rb") as wf:
    sample_rate = wf.getframerate()
    channels = wf.getnchannels()
    sample_width = wf.getsampwidth()
    frames = wf.readframes(wf.getnframes())

audio = np.frombuffer(frames, dtype=np.int16)

print("WAV information")
print("----------------")
print("Sample rate :", sample_rate)
print("Channels    :", channels)
print("Sample width:", sample_width)
print("Samples     :", len(audio))
print()


# Feed audio through the normal openWakeWord streaming path
print("Testing sample...")
print("------------------")

scores = []

chunk_size = 1280

for start in range(0, len(audio), chunk_size):

    chunk = audio[start:start + chunk_size]

    if len(chunk) < chunk_size:
        break

    prediction = model.predict(chunk)

    score = prediction.get("hey_vectoria", 0.0)

    scores.append(score)

    print(f"Chunk {len(scores):2d}: {score:.3f}")


print()
print("==============================")
print(f"Maximum score: {max(scores):.3f}")
print("==============================")