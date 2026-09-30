import numpy as np
import pyaudio
from openwakeword.model import Model


MODEL_PATH = r"C:\Users\Charlson\PycharmProjects\Vectoria\wakeword\training\output\oww_training\hey_vectoria.onnx"

model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

print("Wake-word model loaded!")
print()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

audio = pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)


def record_test(seconds=3):

    scores = []

    chunks = int(RATE / CHUNK * seconds)

    for _ in range(chunks):

        data = stream.read(
            CHUNK,
            exception_on_overflow=False
        )

        audio_data = np.frombuffer(
            data,
            dtype=np.int16
        )

        prediction = model.predict(audio_data)

        score = prediction.get("hey_vectoria", 0.0)

        scores.append(score)

    return max(scores)


try:

    print("========================================")
    print("     VECTORIA WAKE WORD TEST")
    print("========================================")
    print()
    print("For each test:")
    print("1. Press ENTER")
    print("2. Wait for 'SPEAK NOW'")
    print("3. Say the sentence naturally")
    print()
    print("Press Ctrl+C to stop.")
    print()

    test_number = 1

    while True:

        input(f"Test {test_number} - Press ENTER to start...")

        print("SPEAK NOW!")

        max_score = record_test(3)

        print()
        print(f"Maximum confidence: {max_score:.3f}")

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