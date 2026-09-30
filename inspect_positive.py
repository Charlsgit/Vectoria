import wave

files = [
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\0.wav",
    r"wakeword\training\output\oww_training\hey_vectoria\positive_test\1.wav",
]

for file in files:
    with wave.open(file, "rb") as wf:
        print("=" * 50)
        print("File:", file)
        print("Channels:", wf.getnchannels())
        print("Sample rate:", wf.getframerate())
        print("Sample width:", wf.getsampwidth(), "bytes")
        print("Frames:", wf.getnframes())
        print("Duration:", round(wf.getnframes() / wf.getframerate(), 2), "seconds")
