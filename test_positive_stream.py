import numpy as np
import wave
from openwakeword.model import Model

MODEL_PATH = r"wakeword\training\output\oww_training\hey_vectoria.onnx"
AUDIO_PATH = r"wakeword\training\output\oww_training\hey_vectoria\positive_test\0.wav"

model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

with wave.open(AUDIO_PATH, "rb") as wf:
    audio = np.frombuffer(
        wf.readframes(wf.getnframes()),
        dtype=np.int16
    )

CHUNK = 1280

print("Testing generated positive sample in streaming chunks")
print("=" * 60)

scores = []

for start in range(0, len(audio), CHUNK):
    chunk = audio[start:start + CHUNK]

    if len(chunk) < CHUNK:
        break

    prediction = model.predict(chunk)
    score = prediction.get("hey_vectoria", 0.0)
    scores.append(score)

    print(f"Chunk {len(scores):2d}: {score:.3f}")

print("=" * 60)
print(f"Maximum score: {max(scores):.3f}")
