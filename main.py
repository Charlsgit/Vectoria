import time
import threading
import sys
from faster_whisper import WhisperModel
import speech_recognition as sr
import pyttsx3

from PySide6.QtWidgets import QApplication
from vectoria_orb import VectoriaOrb

from ai import ask_ai, warm_up_model
from memory import remember, get_all_memories
from wake_word import (
    start_wake_listener,
    wait_for_wake_word,
    stop_wake_listener,
)

# -------------------------
# Initialize
# -------------------------
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Local offline speech recognition
whisper_model = None

orb = None

recognizer.pause_threshold = 1.0
recognizer.non_speaking_duration = 0.5
recognizer.phrase_threshold = 0.3


def set_orb_state(state):
    """Request an orb state change safely."""
    if orb is not None:
        orb.set_state(state)


# -------------------------
# Text To Speech
# -------------------------

def speak(text):
    set_orb_state("speaking")

    print("Assistant:", text)
    start = time.time()

    engine = None

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

        if female_voice:
            engine.setProperty("voice", female_voice.id)

        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.say(str(text))
        engine.runAndWait()

        print(f"TTS time: {time.time() - start:.2f}s")

    except Exception as e:
        print("TTS ERROR:", e)

    finally:
        if engine is not None:
            try:
                engine.stop()
            except Exception:
                pass


# Register the notification speech callback once.
try:
    from notifications import set_speak_function
    set_speak_function(speak)
except Exception as e:
    print("Notification speech registration warning:", e)


# -------------------------
# Listen to User
# -------------------------

def listen():
    set_orb_state("listening")

    with microphone as source:
        print("Listening...")
        start = time.time()

        try:
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=30,
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

        raw_data = audio.get_raw_data()

        audio_data = np.frombuffer(
            raw_data,
            dtype=np.int16,
        )

        reduced_audio = nr.reduce_noise(
            y=audio_data,
            sr=audio.sample_rate,
            stationary=True,
            prop_decrease=0.8,
        )

        reduced_audio = reduced_audio.astype(
            np.int16
        ).tobytes()

        audio = sr.AudioData(
            reduced_audio,
            audio.sample_rate,
            audio.sample_width,
        )

        print("Noise reduction complete.")

    except Exception as e:
        print("Noise reduction failed:", e)


    # -------------------------
    # Offline Speech Recognition
    # -------------------------

    try:
        import io
        import wave
        import numpy as np

        if whisper_model is None:
            print("Whisper model is not initialized.")
            return ""

        start = time.time()

        # Convert the captured audio to 16 kHz, 16-bit PCM.
        raw_data = audio.get_raw_data(
            convert_rate=16000,
            convert_width=2
        )

        audio_samples = np.frombuffer(
            raw_data,
            dtype=np.int16
        )

        # Build a WAV file in memory for Whisper.
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_samples.tobytes())

        wav_buffer.seek(0)

        segments, info = whisper_model.transcribe(
            wav_buffer,
            language="en",
            beam_size=1,
            vad_filter=True
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        recognition_time = time.time() - start

        print(f"Offline speech recognition: {recognition_time:.2f}s")

        if not text:
            print("I couldn't understand what you said.")
            return ""

        print("You:", text)

        return text.lower()

    except Exception as e:
        print("Offline speech recognition error:", e)
        return ""

# -------------------------
# Main Voice Assistant Loop
# -------------------------

def voice_assistant_loop():

    # Initialize the microphone and model in this thread,
    # after the orb has already appeared.
    try:
        print("Calibrating microphone...")

        with microphone as source:
            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5,
            )

        print("Microphone ready!")

        warm_up_model()

        global whisper_model

        print("Loading offline Whisper STT model...")

        whisper_model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        print("Offline Whisper STT ready!")

    except Exception as e:
        print("Initialization error:", e)
        set_orb_state("idle")
        return

    # -------------------------
    # Continuous Assistant Loop
    # -------------------------

    while True:

        # SLEEP MODE: wait for the wake word
        set_orb_state("idle")

        print("Waiting for 'Hey Vectoria'...")

        try:
            start_wake_listener()
            wait_for_wake_word()

        except Exception as e:
            print("Wake-word listener error:", e)
            set_orb_state("idle")
            break

        finally:
            try:
                stop_wake_listener()
            except Exception as e:
                print("Wake-word stop warning:", e)

        # CONVERSATION MODE
        speak("Yes?")

        while True:

            command = listen()

            # If nothing was understood, keep listening.
            if command == "":
                continue

            # -------------------------
            # End Conversation
            # -------------------------

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
                "shutdown",
            ]

            if command in exit_commands:
                speak("Okay.")
                break

            # -------------------------
            # Save Memory
            # -------------------------

            if command.startswith("remember"):

                print("REMEMBER COMMAND DETECTED!")

                information = command.replace(
                    "remember",
                    "",
                    1,
                ).strip()

                if information.startswith("remember"):
                    information = information.replace(
                        "remember",
                        "",
                        1,
                    ).strip()

                print("Information:", information)

                if information:
                    remember("user_notes", information)
                    speak("Okay, I will remember that.")

                continue

            # -------------------------
            # Memory Lookup
            # -------------------------

            if "what do you remember about me" in command:

                set_orb_state("thinking")
                memories = get_all_memories()

                print("Memories:", memories)

                if memories:
                    memory_text = (
                        "Here is what I remember about you: "
                    )

                    for key, value in memories.items():
                        memory_text += f"{key}: {value}. "

                    speak(memory_text)

                else:
                    speak(
                        "I don't have any memories "
                        "about you yet."
                    )

                continue

            # -------------------------
            # AI Response
            # -------------------------

            set_orb_state("thinking")

            try:
                response = ask_ai(command)
                speak(response)

            except Exception as e:
                print("AI ERROR:", e)
                speak("Sorry, I encountered an error.")

        # Conversation ended; return to sleep mode.
        set_orb_state("idle")


# -------------------------
# Application Entry Point
# -------------------------

if __name__ == "__main__":

    # Qt must run on the main thread.
    app = QApplication(sys.argv)

    # Create and show the orb first.
    orb = VectoriaOrb()
    orb.show()

    # Run voice processing separately.
    voice_thread = threading.Thread(
        target=voice_assistant_loop,
        daemon=True,
    )
    voice_thread.start()

    sys.exit(app.exec())