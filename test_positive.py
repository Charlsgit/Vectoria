import numpy as np
import wave
from openwakeword.model import Model

MODEL_PATH = r"wakeword\training\output\oww_training\hey_vectoria.onnx"

model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

files = [
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\0.wav",
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\1.wav",
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\10.wav",
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\100.wav",
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\101.wav",
]

print("Testing generated POSITIVE samples")
print("=" * 50)

for file in files:
    with wave.open(file, "rb") as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)

    predictions = model.predict(audio)
    score = predictions.get("hey_vectoria", 0.0)

    print(f"{file.split(chr(92))[-1]:8} -> {score:.3f}")
