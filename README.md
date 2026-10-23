# Vectoria 🤖

> A local-first AI voice assistant for natural voice interaction, knowledge retrieval, conversational memory, wake-word activation, and tool-based automation.

## Overview

**Vectoria** is a Python-based AI voice assistant designed to run locally on Windows. It combines speech recognition, a local large language model, Retrieval-Augmented Generation (RAG), conversational memory, text-to-speech, custom wake-word detection, and utility tools in a single application.

The goal is to create a personal AI assistant that can understand spoken commands, retrieve relevant information from a local knowledge base, generate responses using a local LLM, and interact with the user's system through supported tools.

Vectoria uses local models and resources for its core AI pipeline, reducing reliance on cloud-based AI services.

## Features

- 🎙️ **Voice Interaction** — Captures microphone input and processes spoken questions and commands.
- 📴 **Offline Speech Recognition** — Uses Faster-Whisper locally for speech-to-text after the model has been downloaded.
- 🔑 **Custom Wake Word** — Supports activation through the phrase **"Hey Vectoria"** using a custom OpenWakeWord model.
- 🧠 **Local LLM** — Uses Ollama with the `llama3.2:1b` model for local response generation.
- 📚 **Retrieval-Augmented Generation (RAG)** — Retrieves relevant context from local knowledge files before generating knowledge-based answers.
- 🔎 **Semantic Search** — Uses Sentence Transformers embeddings and FAISS similarity search.
- 💾 **Conversational Memory** — Stores and retrieves user information through a local memory system.
- 🔊 **Text-to-Speech** — Uses `pyttsx3` with the Microsoft Zira voice where available.
- 🟣 **Animated Orb Interface** — Uses PySide6 to provide a visual interface for assistant states.
- 🔇 **Noise Reduction** — Applies audio noise reduction during speech processing.
- 🛠️ **Tool Integration** — Supports utility actions through dedicated tools in the project.

## Architecture

The main voice-assistant workflow follows this general pipeline:

```text
                   User Speech
                        |
                        v
               Microphone Capture
                        |
                        v
                Wake-Word Listener
                        |
                        v
              Offline Speech-to-Text
                 Faster-Whisper
                        |
                        v
                Command Processing
                        |
              +---------+---------+
              |                   |
              v                   v
         RAG Retrieval       Tool Handling
              |                   |
              v                   |
        FAISS Search              |
              |                   |
              v                   |
       Relevant Context            |
              +---------+---------+
                        |
                        v
                Local LLM (Ollama)
                        |
                        v
                 Response Handling
                        |
               +--------+--------+
               |                 |
               v                 v
           Local Memory     Text-to-Speech
                                 |
                                 v
                           Spoken Response
```

The exact execution path depends on the user's command. Not every request requires RAG retrieval or tool execution.

## RAG Pipeline

Vectoria uses Retrieval-Augmented Generation to answer questions using information stored in local knowledge files.

```text
Local Knowledge Files
        |
        v
   Text Chunking
        |
        v
Sentence Transformer
    Embeddings
        |
        v
   FAISS Index
        |
        v
 Similarity Search
        |
        v
 Relevant Context
        |
        v
  Local LLM (Ollama)
        |
        v
  Generated Answer
```

### RAG Components

| Component | Technology |
|---|---|
| Embedding model | `all-MiniLM-L6-v2` |
| Vector index | FAISS |
| Knowledge sources | Local `.txt` files |
| Language model | Ollama `llama3.2:1b` |
| Retrieval approach | Embedding-based similarity search |

### Current Knowledge Base

The current knowledge directory includes:

- `knowledge/python.txt`
- `knowledge/statistics.txt`

The knowledge base can be expanded by adding additional supported text files.

## Offline Speech Recognition

Vectoria uses **Faster-Whisper** for local speech-to-text processing.

The current implementation uses:

- Model: `base`
- Device: CPU
- Compute type: INT8
- Language: English

The model must be downloaded before it can be used offline for the first time. Once the required model files and dependencies are available locally, speech transcription does not require an internet connection.

## Wake-Word System

Vectoria includes a custom wake-word detection pipeline for:

**"Hey Vectoria"**

The project includes components for collecting positive and negative audio samples, testing microphone input, and training or evaluating the custom wake-word model.

The runtime model is expected at:

```text
wakeword/training/output/oww_training/hey_vectoria.onnx
```

Training scripts, datasets, and generated artifacts may be maintained locally rather than committed to the public repository.

## Memory

Vectoria includes a local memory system for retaining relevant user information across interactions.

Memory operations are handled through the project's memory module. Runtime memory data is intended to remain local and should not be committed if it contains personal or sensitive information.

## Animated Orb Interface

The visual interface is implemented using **PySide6**.

The orb reflects assistant states such as:

- Idle
- Listening
- Thinking
- Speaking

The interface runs alongside the voice-processing loop.

## Technologies

- **Python**
- **Faster-Whisper** — Offline speech recognition
- **Ollama** — Local LLM execution
- **Llama 3.2 1B** — Local language model
- **Sentence Transformers** — Text embeddings
- **FAISS** — Vector similarity search
- **OpenWakeWord** — Wake-word detection
- **SpeechRecognition** — Microphone capture
- **NumPy** — Audio and numerical processing
- **noisereduce** — Audio noise reduction
- **PySide6** — Desktop orb interface
- **pyttsx3** — Text-to-speech
- **PyAudio** — Microphone input support

## Project Structure

The following is a high-level overview of important project files. The exact repository contents may change as development continues.

```text
Vectoria/
│
├── main.py
├── ai.py
├── rag.py
├── memory.py
├── wake_word.py
├── tools.py
├── notifications.py
├── vectoria_orb.py
├── Launch Vectoria.bat
├── test_offline_stt.py
│
├── knowledge/
│   ├── python.txt
│   └── statistics.txt
│
├── wakeword/
│   └── training/
│       └── output/
│           └── oww_training/
│               └── hey_vectoria.onnx
│
├── README.md
└── .gitignore
```

Some model artifacts, training data, local profiles, and runtime files may be excluded from GitHub.

## Installation and Setup

### Prerequisites

- Windows
- Python compatible with the project's installed dependencies
- Git
- Ollama
- The required Python packages
- A working microphone

### 1. Clone the repository

```powershell
git clone https://github.com/Charlsgit/Vectoria.git
cd Vectoria
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, you can use the virtual environment's Python executable directly without activating it.

### 4. Install dependencies

Install the Python packages required by the project into the virtual environment.

For example, the core packages include:

```powershell
python -m pip install faster-whisper SpeechRecognition pyttsx3 PySide6 sentence-transformers faiss-cpu ollama numpy noisereduce
```

Additional dependencies may be required by the wake-word listener, microphone backend, and other tools. Install the versions compatible with the project before running the application.

> **Note:** If a `requirements.txt` file is added to the repository, prefer installing the pinned dependencies from that file.

### 5. Set up Ollama

Install Ollama and download the model used by Vectoria:

```powershell
ollama pull llama3.2:1b
```

Ensure Ollama is running before launching the assistant.

### 6. Launch Vectoria

From the project root, run:

```powershell
.\.venv\Scripts\python.exe main.py
```

Alternatively, activate `.venv` and run:

```powershell
python main.py
```

Wait for the embedding model, RAG pipeline, AI model, and offline Whisper model to initialize. Then say **"Hey Vectoria"** to activate the assistant.

## Running Offline

Vectoria is designed for local-first operation. To use the core assistant without internet access:

1. Download all required AI models and dependencies while online.
2. Confirm that the embedding model and Faster-Whisper model are cached locally.
3. Download the required Ollama model.
4. Ensure the wake-word model and local knowledge files are present.
5. Run Vectoria with Wi-Fi disabled and test the complete workflow.

Offline operation depends on the availability of every required runtime component. Features that rely on external websites, online APIs, or network services will not work without a suitable connection.

## Project Status

Vectoria is an actively developed project.

Current implementation areas include:

- Local voice interaction
- Offline speech recognition
- Custom wake-word detection
- Local LLM integration
- RAG-based knowledge retrieval
- Conversational memory
- Text-to-speech
- Animated desktop interface
- Tool-based interaction

Individual components may continue to be refined and tested as the project develops.

## Future Improvements

Potential improvements include:

- Improved wake-word accuracy
- More robust noise handling
- Better conversational context management
- Expanded local knowledge sources
- Additional tools and system automation
- Improved response generation
- Further optimization for low-resource computers
- A mobile interface and laptop integration

These are development goals and should not be interpreted as completed features.

## Author

**Yarasani Charlson**

B.Tech Computer Science (Data Science)

GitHub: [@Charlsgit](https://github.com/Charlsgit)

---

⭐ If you find Vectoria interesting, explore the repository and follow its development.
