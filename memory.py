import json
import os


# ============================================================
# Memory File
# ============================================================

MEMORY_FILE = os.path.join(
    os.path.dirname(__file__),
    "memory.json"
)


# ============================================================
# Load Memory
# ============================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read().strip()

            if not content:
                return {}

            return json.loads(content)

    except (json.JSONDecodeError, OSError) as e:

        print("Memory load error:", e)

        return {}


# ============================================================
# Get All Memories
# ============================================================

def get_all_memories():

    return load_memory()


# ============================================================
# Save Memory
# ============================================================

def save_memory(memory):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as e:

        print("Memory save error:", e)

        return False


# ============================================================
# Generic Memory
# ============================================================

def remember(key, value):

    memory = load_memory()

    if key not in memory:
        memory[key] = []

    # Make sure this key is actually a list
    if not isinstance(memory[key], list):

        memory[key] = [
            memory[key]
        ]

    if value not in memory[key]:

        memory[key].append(value)

    save_memory(memory)


# ============================================================
# Recall Generic Memory
# ============================================================

def recall(key):

    memory = load_memory()

    return memory.get(key)


# ============================================================
# Save Preference
# ============================================================

def remember_preference(category, value):

    memory = load_memory()

    if "preferences" not in memory:
        memory["preferences"] = {}

    if not isinstance(
        memory["preferences"],
        dict
    ):
        memory["preferences"] = {}

    memory["preferences"][category] = value

    save_memory(memory)

    print(
        "Preference saved:",
        category,
        "=",
        value
    )


# ============================================================
# Recall Preference
# ============================================================

def recall_preference(category):

    memory = load_memory()

    preferences = memory.get(
        "preferences",
        {}
    )

    if not isinstance(preferences, dict):
        return None

    return preferences.get(category)


# ============================================================
# Save User Note
# ============================================================

def remember_note(note):

    memory = load_memory()

    if "user_notes" not in memory:
        memory["user_notes"] = []

    if not isinstance(
        memory["user_notes"],
        list
    ):
        memory["user_notes"] = []

    if note not in memory["user_notes"]:

        memory["user_notes"].append(note)

    save_memory(memory)

    print(
        "User note saved:",
        note
    )


# ============================================================
# Recall User Notes
# ============================================================

def get_user_notes():

    memory = load_memory()

    notes = memory.get(
        "user_notes",
        []
    )

    if not isinstance(notes, list):
        return []

    return notes


# ============================================================
# User Name
# ============================================================

def get_user_name():

    memory = load_memory()

    return memory.get("name")


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    remember(
        "test",
        "This is a memory test."
    )

    print("Memory saved!")

    print(
        load_memory()
    )