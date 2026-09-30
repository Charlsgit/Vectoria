import ollama

response = ollama.chat(
    model="llama3.2:1b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a voice assistant. "
                "Answer briefly in 1 or 2 sentences. "
                "No headings. No lists. No extra explanation."
            )
        },
        {
            "role": "user",
            "content": "Tell me about machine learning."
        }
    ],
    options={
        "num_predict": 60,
        "temperature": 0.2
    }
)

print("\nMODEL RESPONSE:\n")
print(response["message"]["content"].strip())