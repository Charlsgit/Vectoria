import numpy as np
import pyaudio
from openwakeword.model import Model


MODEL_PATH = (
    r"C:\Users\Charlson\PycharmProjects\Vectoria"
    r"\wakeword\training\output\oww_training\hey_vectoria.onnx"
)

WAKE_WORD = "hey_vectoria"
THRESHOLD = 0.5

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280


model = Model(
    inference_framework="onnx",
    wakeword_models=[MODEL_PATH]
)

audio = None
stream = None


def start_wake_listener():
    global audio, stream

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )


def wait_for_wake_word():
    print("Waiting for 'Hey Vectoria'...")

    while True:
        data = stream.read(
            CHUNK,
            exception_on_overflow=False
        )

        audio_data = np.frombuffer(
            data,
            dtype=np.int16
        )

        print(
            f"Audio: min={audio_data.min()}, "
            f"max={audio_data.max()}, "
            f"RMS={np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)):.1f}"
        )

        prediction = model.predict(audio_data)

        score = prediction.get(
            WAKE_WORD,
            0.0
        )

        print(f"Wake score: {score:.3f}")

        if score >= THRESHOLD:
            print(
                f"Wake word detected! "
                f"Confidence: {score:.3f}"
            )

            return True


def stop_wake_listener():
    global audio, stream

    if stream is not None:
        stream.stop_stream()
        stream.close()
        stream = None

    if audio is not None:
        audio.terminate()
        audio = None