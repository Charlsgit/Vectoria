import wave
import numpy as np
from scipy.signal import resample_poly
from openwakeword.model import Model


MODEL_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\wakeword\training\output\oww_training\hey_vectoria_before_10000.onnx"
WAV_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\live_test_2sec.wav"

model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

print("Wake-word model loaded!")
print()


with wave.open(WAV_PATH, "rb") as wf:

    rate = wf.getframerate()
    channels = wf.getnchannels()
    sample_width = wf.getsampwidth()
    frames = wf.readframes(wf.getnframes())


print("WAV information:")
print("Sample rate:", rate)
print("Channels:", channels)
print("Sample width:", sample_width)
print()


audio = np.frombuffer(
    frames,
    dtype=np.int16
)

print("Original Peak:", np.max(np.abs(audio)))
print(
    "Original RMS:",
    np.sqrt(np.mean(audio.astype(np.float64) ** 2))
)


# 48 kHz -> 16 kHz
audio_16k = resample_poly(audio, up=1, down=3)

# Normalize/amplify audio
audio_float = audio_16k.astype(np.float32)

peak = np.max(np.abs(audio_float))

if peak > 0:
    audio_float = audio_float / peak
    audio_float = audio_float * 12000

audio_16k = np.clip(audio_float, -32768, 32767).astype(np.int16)

print("Normalized Peak:", np.max(np.abs(audio_16k)))
print("Normalized RMS:", np.sqrt(np.mean(audio_16k.astype(np.float64) ** 2)))

print("Resampled samples:", len(audio_16k))
print()


# Feed audio to model in 1280-sample chunks
CHUNK = 1280
scores = []

for start in range(0, len(audio_16k) - CHUNK + 1, CHUNK):

    chunk = audio_16k[start:start + CHUNK]

    prediction = model.predict(chunk)

    score = prediction.get(
        "hey_vectoria",
        0.0
    )

    scores.append(score)

    print(
        f"Chunk {start // CHUNK:03d}: {score:.3f}"
    )


print()
print("========================================")

if scores:
    max_score = max(scores)
else:
    max_score = 0.0

print(f"Maximum confidence: {max_score:.3f}")

if max_score >= 0.5:
    print(">>> WAKE WORD DETECTED")
else:
    print(">>> NOT DETECTED")

print("========================================")