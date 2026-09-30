import numpy as np
import pyaudio
from scipy.signal import resample_poly
from openwakeword.model import Model


MODEL_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\wakeword\training\output\oww_training\hey_vectoria.onnx"

DEVICE_INDEX = 9
INPUT_RATE = 48000
MODEL_RATE = 16000
CHUNK_48K = 3840

print("Model path:", MODEL_PATH)

model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

print("Wake-word model loaded!")
print(f"Using microphone device: {DEVICE_INDEX}")
print(f"Input rate: {INPUT_RATE} Hz")
print(f"Model rate: {MODEL_RATE} Hz")
print()

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=INPUT_RATE,
    input=True,
    input_device_index=DEVICE_INDEX,
    frames_per_buffer=CHUNK_48K
)


def record_test(seconds=3):

    scores = []

    chunks = int(INPUT_RATE / CHUNK_48K * seconds)

    for _ in range(chunks):

        data = stream.read(
            CHUNK_48K,
            exception_on_overflow=False
        )

        audio_48k = np.frombuffer(
            data,
            dtype=np.int16
        )

        # Convert 48 kHz -> 16 kHz
        audio_16k = resample_poly(
            audio_48k,
            up=1,
            down=3
        )

        audio_16k = np.asarray(
            audio_16k,
            dtype=np.int16
        )

        prediction = model.predict(audio_16k)

        score = prediction.get(
            "hey_vectoria",
            0.0
        )

        scores.append(score)

        print(f"{score:.3f}", end=" ")

    print()

    return max(scores)


try:

    print("========================================")
    print(" VECTORIA WAKE WORD RESAMPLING TEST")
    print("========================================")
    print()
    print("Say 'Hey Vectoria' naturally.")
    print()

    test_number = 1

    while True:

        input(
            f"Test {test_number} - Press ENTER to start..."
        )

        print("SPEAK NOW!")

        max_score = record_test(3)

        print()
        print(
            f"Maximum confidence: {max_score:.3f}"
        )

        if max_score >= 0.5:
            print(">>> WAKE WORD DETECTED")
        else:
            print(">>> NOT DETECTED")

        print("----------------------------------------")
        print()

        test_number += 1


except KeyboardInterrupt:

    print("\nStopping test...")


finally:

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Test stopped.")