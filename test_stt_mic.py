import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone(device_index=2)

print("Using:", sr.Microphone.list_microphone_names()[2])

with m as source:
    print("Calibrating...")
    r.adjust_for_ambient_noise(source, duration=1)
    print("Speak now...")
    audio = r.listen(source, timeout=10, phrase_time_limit=5)

print("Audio captured!")
print("Trying speech recognition...")

try:
    text = r.recognize_google(audio)
    print("YOU SAID:", text)
except Exception as e:
    print("ERROR:", type(e).__name__, e)
