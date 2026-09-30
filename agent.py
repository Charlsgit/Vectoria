import ollama
from tools import TOOLS
from ai import execute_tool


# -------------------------
# Agent Decision
# -------------------------

def decide_action(question):

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": """
You are a tool selection agent.

Available tool:
calculator

Rules:
- Mathematical questions MUST use calculator.
- Non-mathematical questions must return none.

Output ONLY one line.

Format:
calculator | expression

or:
none

Examples:

User: 25 * 48
Output: calculator | 25 * 48

User: What is 100 / 5?
Output: calculator | 100 / 5

User: What is 75 + 25?
Output: calculator | 75 + 25

User: Hello
Output: none
"""
            },
            {
                "role": "user",
                "content": question
            }
        ],
        options={
            "temperature": 0,
            "num_predict": 50
        }
    )

    result = response["message"]["content"].strip()

    return result

# -------------------------
# Parse Agent Action
# -------------------------

def parse_action(action):

    parts = action.split("|", 1)

    if len(parts) != 2:
        return None, None

    tool_name = parts[0].strip().lower()
    tool_input = parts[1].strip()

    return tool_name, tool_input

# -------------------------
# Generate Final Answer
# -------------------------

def generate_final_answer(question, tool_name, tool_result):

    prompt = f"""
You are an AI assistant.

The user asked:

{question}

The agent used this tool:

{tool_name}

The tool returned:

{tool_result}

Use the tool result to answer the user's original question.

Answer naturally and concisely.
Do not mention internal tools, parsing, or agent steps.
"""

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0,
            "num_predict": 100
        }
    )

    return response["message"]["content"].strip()


if __name__ == "__main__":

    print("Agent Test")
    print("Type 'exit' to stop.")

    while True:

        question = input("\n> ")

        if question.lower().strip() == "exit":
            break

        print("\nAgent thinking...")

        # -------------------------
        # Step 1: Decide Action
        # -------------------------

        action = decide_action(question)

        print("LLM Action:", action)

        # -------------------------
        # Step 2: Parse Action
        # -------------------------

        tool_name, tool_input = parse_action(action)

        print("Tool:", tool_name)
        print("Input:", tool_input)

        # -------------------------
        # Step 3: Execute Tool
        # -------------------------

        if tool_name:

            result = execute_tool(
                tool_name,
                tool_input
            )

            print("Tool Result:", result)

            # -------------------------
            # Step 4: Generate Answer
            # -------------------------

            final_answer = generate_final_answer(
                question,
                tool_name,
                result
            )

            print("\nAgent Answer:")
            print(final_answer)

        else:

            print("\nAgent Answer:")
            print("I don't need a tool for this request.")