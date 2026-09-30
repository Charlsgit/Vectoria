**VECTORIA (persistent contextual AI assistant)**

It is an engine that is  privacy-focused, local-first personal AI agent that combines memory, context, intelligent RAG, smart routing, voice, and agentic capabilities in one system.

    What Existing solutions can't do:

                    Google Search
                          ↓
            doesn't know private information


                       ChatGPT
                          ↓
    doesn't inherently know your organizational context


                    RAG chatbot
                          ↓
       usually doesn't maintain deep conversational context


                    Voice assistant
                          ↓
      usually doesn't understand private domain knowledge



    Vectoria:
                     VECTORIA
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
    Private Knowledge  Memory        Voice
         │              │              │
         └──────────────┼──────────────┘
                        ↓
                 Context Engine
                        ↓
               Intelligent Router
                        ↓
                   LLM / Tools
                        ↓
               Personalized Action

FEATURES:

• **Local-first AI** – Runs LLM locally for privacy and offline capability.

• **Personal Memory** – Remembers user-specific information across sessions.

• **Intelligent RAG** – Retrieves only relevant knowledge instead of blindly using documents.

• **Smart Question Routing** – Automatically decides between RAG, memory, and general AI.

• **Conversation Context** – Understands follow-up questions and previous conversation.

• **Multi-source Knowledge** – Can work with multiple personal knowledge documents.

• **Voice Interaction** – Natural voice input and spoken responses.

• **Grounded Answers** – Uses retrieved knowledge to reduce hallucinations.

• **Agentic Architecture** – Designed to evolve from chatbot into an autonomous AI agent.

• **Tool/Action Integration** – Can eventually perform real-world tasks, not just answer questions.

• **Guardrails** – Planned safety, input validation, prompt-injection protection and output checking.

• **Lightweight & Resource-Aware** – Designed to run on consumer hardware rather than requiring expensive cloud infrastructure.



FILE OVERVIEW

**main.py** → overall execution flow

**agent.py** → decision/router logic

**ai.py** → Ollama/LLM calls

**rag.py** → retrieval

**memory.py** → memory operations

**tools.py** → calculator & Time

**app.py** → Streamlit interface


    General RAG:

            Knowledge Documents
                    ↓
                Chunking
                    ↓
                Embedding
                    ↓
              Vector Storage [ FAISS(Facebook AI Similarity Search) ]
                    ↓
                Retrieval
                    ↓
            Augmented Prompt
                    ↓
             LLM Generation
                    ↓
                  Answer

**1) Ingestion Phase (Preparation):** .txt
    (PDFs, text files, databases) → smaller chunks [create_chunks()] →
    embedding model(all-MiniLM-L6-v2) [Embedding library - Sentence Transformer](text → numerical vectors) → vector database(FAISS)

**2) Retrieval Phase (Search):** index.search()
    Question (query → vector → search vector database) → document chunks → →→