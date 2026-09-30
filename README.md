# Vectoria 🤖

> A local AI voice assistant designed to combine voice interaction, RAG-based knowledge retrieval, memory, wake-word detection, and tool-based interaction.

## Overview

Vectoria is a locally running AI voice assistant that allows users to interact with an AI system through natural voice conversations.

The project combines speech recognition, local language-model generation, retrieval-augmented generation (RAG), conversational memory, text-to-speech, wake-word detection, and utility tools into a single assistant.

The system is designed to run locally on a Windows machine rather than depending entirely on cloud-based AI services.

## Features

- 🎙️ **Voice Interaction**  
  Capture user speech and process spoken commands and questions.

- 🧠 **Local AI Processing**  
  Uses locally available AI models for language generation.

- 📚 **RAG (Retrieval-Augmented Generation)**  
  Retrieves relevant information from a local knowledge base before generating responses.

- 💾 **Conversational Memory**  
  Maintains relevant conversation information using a local memory system.

- 🔊 **Text-to-Speech**  
  Converts generated responses into spoken output.

- 🗣️ **Wake-Word Detection**  
  Supports activation through the custom wake word **"Hey Vectoria"**.

- 🛠️ **Tool Interaction**  
  Provides functionality through dedicated tools rather than relying only on conversational responses.

- 📖 **Knowledge Base**  
  Supports local knowledge files that can be embedded and searched for relevant information.

## Architecture

The core Vectoria pipeline can be represented as:

```
                    ┌──────────────────┐
                    │   User Speech    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │Speech Recognition│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Intent / Query   │
                    │    Processing    │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
        ┌─────────────────┐     ┌─────────────────┐
        │   RAG Search    │     │  Tool Selection │
        │ Local Knowledge │     │                 │
        └────────┬────────┘     └────────┬────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Local LLM      │
                    │    Generation    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Memory / Context │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Text-to-Speech │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Spoken Reply   │
                    └──────────────────┘
```

# RAG Pipeline

Vectoria uses a local retrieval pipeline for knowledge-based questions.

```
Knowledge Files
      │
      ▼
Text Chunking
      │
      ▼
Sentence Transformer Embeddings
      │
      ▼
FAISS Vector Index
      │
      ▼
Similarity Search
      │
      ▼
Relevant Context
      │
      ▼
Local LLM
      │
      ▼
Generated Response

```
The current knowledge base includes topics such as:

-  **Python**

-  **Statistics**

The knowledge files can be expanded with additional information as the project develops.

# Memory

Vectoria includes a local conversational memory system.

Memory is stored locally and can be used to maintain relevant context across interactions.

Runtime memory files are intentionally excluded from the public GitHub repository through ```.gitignore.```

# Wake-Word System

Vectoria includes a custom wake-word pipeline for:

```Hey Vectoria```

The wake-word system contains components for:

- **Recording positive samples**
- **Recording negative samples**
- **Wake-word testing**
- **Microphone testing**
- **Streaming detection**
- **Resampling**
- **Pipeline testing**

Training datasets and generated model artifacts are excluded from the GitHub repository.

# Project Structure

```
Vectoria/
│
├── agent.py
├── ai.py
├── app.py
├── conversation.py
├── main.py
├── memory.py
├── notifications.py
├── rag.py
├── realtime.py
├── tools.py
├── wake_word.py
│
├── knowledge/
│   ├── python.txt
│   └── statistics.txt
│
├── wakeword/
│   ├── record_negative.py
│   ├── record_positive.py
│   ├── record_wakeword.py
│   ├── test_exact_pipeline.py
│   ├── test_microphone.py
│   ├── test_streaming.py
│   ├── test_wakeword.py
│   ├── test_wakeword_resampled.py
│   └── test_wakeword_wav.py
│
├── test_live_mic.py
├── test_model.py
├── test_model_features.py
├── test_positive.py
├── test_positive_stream.py
├── test_stt_mic.py
│
├── .gitignore
├── Track.md
└── Overview of the project sctucture.md
```

# Technologies

The project currently uses technologies and components including:

- **Python**
- **PyTorch**
- **Ollama**
- **Local LLM models**
- **Sentence Transformers**
- **FAISS**
- **Speech Recognition**
- **Text-to-Speech**
- **OpenWakeWord**
- **NumPy**
- **PyAudio / microphone input**
- **Streamlit**
  
# Local-First Design

Vectoria is designed around a local-first approach.

The goal is to keep the core assistant functionality running on the user's own machine, including:

- **AI model execution**
- **Knowledge retrieval**
- **Memory**
- **Voice processing**
- **Wake-word detection**
- **Tool execution**

This approach provides greater control over the local environment and allows the assistant to operate without making every interaction dependent on a cloud service.

# Running the Project

Clone the repository:

```
git clone https://github.com/Charlsgit/Vectoria.git
cd Vectoria
```

Create a virtual environment:
```
python -m venv .venv
```

Activate it on Windows:
```
.venv\Scripts\activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```
```
Note: A requirements.txt file will be added as the project dependency setup is finalized.
```

# Project Status

Vectoria is an actively developed project.

Current development areas include:

- **Voice interaction**
- **Local LLM integration**
- **RAG-based knowledge retrieval**
- **Conversational memory**
- **Wake-word detection**
- **Tool interaction**
- **Assistant automation**
- **Natural-language command processing**

Some components are still being refined and tested as the project evolves.

# Future Improvements

Planned improvements include:

- **More natural-language tool commands**
- **Improved wake-word accuracy**
- **Better conversational context handling**
- **Additional knowledge sources**
- **More assistant tools**
- **Improved response generation**
- **Better integration between voice, memory, RAG, and tools**
- **Further optimization for local execution**

## Author

**Yarasani Charlson**

B.Tech Computer Science (Data Science)

⭐ If you find the project interesting, feel free to explore the repository and follow its development.
