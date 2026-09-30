import time
import speech_recognition as sr
import pyttsx3

from ai import ask_ai, warm_up_model
from memory import remember, get_all_memories
from wake_word import start_wake_listener, wait_for_wake_word, stop_wake_listener

# -------------------------
# Initialize
# -------------------------

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# How quickly speech is considered finished

recognizer.pause_threshold = 1.0
recognizer.non_speaking_duration = 0.5
recognizer.phrase_threshold = 0.3

print("Calibrating microphone...")

with microphone as source:

    recognizer.adjust_for_ambient_noise(
        source,
        duration=0.5
    )

print("Microphone ready!")
warm_up_model()

# -------------------------
# Text To Speech
# -------------------------

def speak(text):

    print("Assistant:", text)

    start = time.time()

    try:

        # Create a fresh SAPI5 engine
        engine = pyttsx3.init("sapi5")

        # Find Microsoft Zira
        voices = engine.getProperty("voices")

        female_voice = None

        for voice in voices:

            if "zira" in voice.name.lower():
                female_voice = voice
                break

        # Select Zira
        if female_voice:

            engine.setProperty(
                "voice",
                female_voice.id
            )

        engine.setProperty(
            "rate",
            175
        )

        engine.setProperty(
            "volume",
            1.0
        )

        # Speak
        engine.say(text)

        engine.runAndWait()

        from notifications import set_speak_function

        set_speak_function(speak)

        # Stop and release the engine
        engine.stop()

        print(
            f"TTS time: "
            f"{time.time() - start:.2f}s"
        )

    except Exception as e:

        print(
            "TTS ERROR:",
            e
        )

# -------------------------
# Listen to User
# -------------------------

def listen():

    with microphone as source:

        print("Listening...")

        start = time.time()

        try:

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=30
            )

        except sr.WaitTimeoutError:

            print("No speech detected.")

            return ""

        listen_time = time.time() - start
        print(f"Listening capture: {listen_time:.2f}s")

    # -------------------------
    # Noise Reduction
    # -------------------------

    try:

        import numpy as np
        import noisereduce as nr

        print("Applying noise reduction...")

        # Convert SpeechRecognition AudioData
        # into raw PCM bytes
        raw_data = audio.get_raw_data()

        # Convert bytes to numpy array
        audio_data = np.frombuffer(
            raw_data,
            dtype=np.int16
        )

        # Noise reduction
        reduced_audio = nr.reduce_noise(
            y=audio_data,
            sr=audio.sample_rate,
            stationary=True,
            prop_decrease=0.8
        )

        # Convert back to bytes
        reduced_audio = reduced_audio.astype(
            np.int16
        ).tobytes()

        # Create new AudioData object
        audio = sr.AudioData(
            reduced_audio,
            audio.sample_rate,
            audio.sample_width
        )

        print("Noise reduction complete.")

    except Exception as e:

        print(
            "Noise reduction failed:",
            e
        )

    # -------------------------
    # Speech Recognition
    # -------------------------

    try:

        start = time.time()

        text = recognizer.recognize_google(
            audio
        )

        recognition_time = time.time() - start

        print(
            f"Speech recognition: "
            f"{recognition_time:.2f}s"
        )

        print("You:", text)

        return text.lower()

    except sr.UnknownValueError:

        print(
            "I couldn't understand "
            "what you said."
        )

        return ""

    except sr.RequestError:

        speak(
            "Sorry, the speech recognition "
            "service is unavailable."
        )

        return ""


# -------------------------
# Main Program
# -------------------------

while True:

    # =====================================
    # SLEEP MODE
    # Wait for "Hey Vectoria"
    # =====================================

    start_wake_listener()

    print("Waiting for 'Hey Vectoria'...")

    wait_for_wake_word()

    stop_wake_listener()

    # =====================================
    # CONVERSATION MODE
    # =====================================

    speak("Yes?")

    while True:

        command = listen()

        # If nothing was understood, keep
        # conversation mode active
        if command == "":
            continue

        # =================================
        # END CONVERSATION
        # =================================

        exit_commands = [
            "ok",
            "okay",
            "ok stop",
            "okay stop",
            "stop",
            "stop listening",
            "goodbye",
            "bye",
            "exit",
            "quit",
            "shutdown"
        ]

        if command in exit_commands:

            speak("Okay.")

            # Leave conversation mode
            # and return to sleep mode
            break

        # =================================
        # MEMORY
        # =================================

        if command.startswith("remember"):

            print("REMEMBER COMMAND DETECTED!")

            information = command.replace(
                "remember",
                "",
                1
            ).strip()

            # Clean accidental extra "remember"
            if information.startswith("remember"):

                information = information.replace(
                    "remember",
                    "",
                    1
                ).strip()

            print("Information:", information)

            if information:

                remember(
                    "user_notes",
                    information
                )

                speak(
                    "Okay, I will remember that."
                )

            continue

        # =================================
        # MEMORY LOOKUP
        # =================================

        if "what do you remember about me" in command:

            memories = get_all_memories()

            print("Memories:", memories)

            if memories:

                memory_text = (
                    "Here is what I remember about you: "
                )

                for key, value in memories.items():

                    memory_text += (
                        f"{key}: {value}. "
                    )

                speak(memory_text)

            else:

                speak(
                    "I don't have any memories "
                    "about you yet."
                )

            continue

        # =================================
        # AI
        # =================================

        response = ask_ai(command)

        speak(response)

    # =====================================
    # Conversation ended.
    #
    # The inner loop broke, so we reach
    # here and automatically go back to
    # the outer loop → SLEEP MODE.
    # =====================================