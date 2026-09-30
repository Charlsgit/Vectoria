import wave
import numpy as np
import openwakeword.model as oww

MODEL = "wakeword/training/output/oww_training/hey_vectoria.onnx"
AUDIO = "wakeword/training/output/oww_training/hey_vectoria/positive_test/0.wav"

model = oww.Model(wakeword_models=[MODEL])

with wave.open(AUDIO, "rb") as f:
    print("Audio:", f.getnchannels(), "ch,", f.getframerate(), "Hz,", f.getsampwidth() * 8, "bit")

    chunk = 1280
    scores = []
    i = 0

    data = f.readframes(chunk)

    while data:
        i += 1

        audio = np.frombuffer(data, dtype=np.int16)
        prediction = model.predict(audio)
        score = list(prediction.values())[0]

        scores.append(score)
        print(f"Chunk {i}: {score:.3f}")

        data = f.readframes(chunk)

print(f"\nMAX SCORE: {max(scores):.3f}")
