conversation = []

conversation_state = {
    "current_topic": None,
    "entities": {},
    "previous_topics": [],
    "last_entity": None,
    "context_history": []
}

# -----------------------------------
# Add conversation message
# -----------------------------------

def add_message(role, content):

    conversation.append({
        "role": role,
        "content": content
    })


# -----------------------------------
# Get recent conversation
# -----------------------------------

def get_recent_conversation(limit=6):

    recent = conversation[-limit:]

    print(
        "Short-term memory:",
        len(recent),
        "messages"
    )

    return recent

# -----------------------------------
# Format Conversation History
# -----------------------------------

def format_conversation_history(limit=6):

    recent = conversation[-limit:]

    if not recent:
        return ""

    history = []

    for message in recent:

        role = message["role"].capitalize()
        content = message["content"]

        history.append(
            f"{role}: {content}"
        )

    return "\n".join(history)

# -----------------------------------
# Search Conversation History
# -----------------------------------

def search_conversation_history(keyword):

    if not keyword:
        return []

    keyword = keyword.lower()

    matches = []

    for message in conversation:

        if keyword in message["content"].lower():

            matches.append(message)

    return matches

# -----------------------------------
# Build Context Summary
# -----------------------------------

def get_context_summary():

    topic = get_current_topic()
    history = get_context_history()

    summary = {
        "current_topic": topic,
        "recent_entities": [],
        "conversation": get_recent_conversation()
    }

    # Get recent context items
    for item in reversed(history):

        if item["entity_type"] != "topic":

            summary["recent_entities"].append({
                "type": item["entity_type"],
                "entity": item["entity"],
                "topic": item["topic"]
            })

        # Keep summary small
        if len(summary["recent_entities"]) >= 5:
            break

    return summary

# -----------------------------------
# Get last user message
# -----------------------------------

def get_last_user_message():

    for message in reversed(conversation):

        if message["role"] == "user":
            return message["content"]

    return None


# -----------------------------------
# Get last assistant message
# -----------------------------------

def get_last_assistant_message():

    for message in reversed(conversation):

        if message["role"] == "assistant":
            return message["content"]

    return None


# -----------------------------------
# Topic Management
# -----------------------------------

def set_current_topic(topic):

    topic = topic.strip()

    if conversation_state["current_topic"] != topic:

        old_topic = conversation_state["current_topic"]

        if old_topic:
            conversation_state["previous_topics"].append(old_topic)

        conversation_state["current_topic"] = topic

        # Automatically add topic to context history
        add_context_history(
            topic=topic,
            entity_type="topic",
            entity=topic
        )

    print("Current topic:", topic)

def get_current_topic():

    return conversation_state["current_topic"]


# -----------------------------------
# Entity Management
# -----------------------------------

def add_entity(entity_type, value):

    if not value:
        return

    value = value.strip()

    conversation_state["entities"][entity_type] = value

    # Track the most recently mentioned entity
    conversation_state["last_entity"] = {
        "type": entity_type,
        "value": value
    }

    print(
        "Entity:",
        entity_type,
        "=",
        value
    )

def get_last_entity():

    return conversation_state["last_entity"]

# -----------------------------------
# Conversation Context History
# -----------------------------------

def add_context_history(topic=None, entity_type=None, entity=None):

    history_item = {
        "topic": topic,
        "entity_type": entity_type,
        "entity": entity
    }

    conversation_state["context_history"].append(
        history_item
    )

    print(
        "Context history added:",
        history_item
    )

def get_context_history():

    return conversation_state["context_history"]

def get_last_context(entity_type=None):

    history = conversation_state["context_history"]

    if not history:
        return None

    # Search from newest to oldest
    for item in reversed(history):

        if entity_type is None:
            return item

        if item["entity_type"] == entity_type:
            return item

    return None

# -----------------------------------
# Track Multiple Entities
# -----------------------------------

def track_entity(entity_type, value):

    if entity_type not in conversation_state["entities"]:
        conversation_state["entities"][entity_type] = []

    if value not in conversation_state["entities"][entity_type]:
        conversation_state["entities"][entity_type].append(value)

    conversation_state["last_entity"] = {
        "type": entity_type,
        "value": value
    }

    # Automatically add entity to context history
    add_context_history(
        topic=conversation_state["current_topic"],
        entity_type=entity_type,
        entity=value
    )

    print(
        f"Entity tracked: {entity_type} = {value}"
    )

# -----------------------------------
# Detect Entity Type
# -----------------------------------

def detect_entity(question):

    question_lower = question.lower()

    # People
    person_patterns = [
        "who created",
        "who invented",
        "who developed",
        "who introduced",
        "who founded"
    ]

    for pattern in person_patterns:

        if pattern in question_lower:

            return "person"

    # Technologies
    technology_patterns = [
        "python",
        "tensorflow",
        "pytorch",
        "ollama",
        "faiss"
    ]

    for technology in technology_patterns:

        if technology in question_lower:

            return "technology"

    return None

# -----------------------------------
# Follow-up Detection
# -----------------------------------

def detect_follow_up(question):

    question_lower = question.lower().strip()

    # --------------------------------
    # Pronouns / possessives
    # --------------------------------

    follow_up_words = [
        "it",
        "its",
        "they",
        "them",
        "their",
        "this",
        "that",
        "these",
        "those",
        "he",
        "she",
        "his",
        "her"
    ]

    words = [
        word.strip("?!.,'\"")
        for word in question_lower.split()
    ]

    if any(
        word in follow_up_words
        for word in words
    ):
        return True

    # --------------------------------
    # Follow-up phrases
    # --------------------------------

    follow_up_phrases = [
        "what about",
        "how about",
        "and what",
        "and how",
        "and why",
        "and when",
        "and where",
        "what else",
        "tell me more",
        "more about",
        "why is that",
        "how so",

        # Incomplete follow-ups
        "give me an example of",
        "give me another example of",
        "an example of",
        "example of",
        "give an example of",
        "show me an example of",
        "give me an example",
        "give me another example",
        "another example",
        "more examples"
    ]

    if any(
        phrase in question_lower
        for phrase in follow_up_phrases
    ):
        return True

    return False

# -----------------------------------
# Extract Topic
# -----------------------------------

def extract_topic(question):

    question_lower = question.lower().strip()

    # --------------------------------
    # Personal / memory questions
    # --------------------------------
    # These should NOT become topics.
    # They are handled by memory.py / ai.py.
    # --------------------------------

    personal_patterns = [
        # Identity
        "what is my name",
        "what's my name",
        "who am i",
        "what is the user's name",
        "what's the user's name",

        # Personal memory / preferences
        "what is my favourite",
        "what's my favourite",
        "what are my favourite",
        "what is my favorite",
        "what's my favorite",
        "what are my favorite",

        # Personal profile
        "what are my qualifications",
        "what is my qualification",
        "where am i studying",
        "what am i studying",
        "what did i study",
        "where did i study",
        "what is my education",
        "what are my skills",
        "what is my background"
    ]

    if any(
        pattern in question_lower
        for pattern in personal_patterns
    ):
        return None

    patterns = [
        "what is ",
        "what are ",
        "what's ",
        "tell me about ",
        "explain ",
        "define ",
        "describe ",
        "what do you mean by "
    ]

    follow_up_words = [
        "it",
        "its",
        "they",
        "them",
        "their",
        "this",
        "that",
        "these",
        "those",
        "he",
        "she",
        "his",
        "her"
    ]

    for pattern in patterns:

        if question_lower.startswith(pattern):

            topic = question_lower[
                len(pattern):
            ]

            topic = topic.rstrip(
                "?!.,"
            ).strip()

            if not topic:
                return None

            # --------------------------------
            # Do not treat pronoun-based
            # questions as new topics
            # --------------------------------

            words = topic.split()

            if any(
                    word.strip("?!.,'\"")
                    in follow_up_words
                    for word in words
            ):
                return None

            # --------------------------------
            # Normalize topic to the core entity
            # --------------------------------
            # Examples:
            # Python's advantages -> Python
            # Python's features -> Python
            # Python advantages  -> Python
            # Java's applications -> Java
            # --------------------------------

            topic_words = topic.split()

            if len(topic_words) > 1:

                core_topic = topic_words[0]

                # Remove possessive "'s"
                core_topic = core_topic.rstrip(
                    "?!.,'\""
                )

                if core_topic.endswith("'s"):
                    core_topic = core_topic[:-2]

                # Common descriptive/question suffixes
                topic_suffixes = [
                    "advantages",
                    "benefits",
                    "features",
                    "uses",
                    "usage",
                    "applications",
                    "limitations",
                    "disadvantages",
                    "types",
                    "examples",
                    "characteristics",
                    "importance",
                    "history",
                    "background"
                ]

                remaining_words = [
                    word.strip("?!.,'\"")
                    for word in topic_words[1:]
                ]

                if any(
                        suffix in remaining_words
                        for suffix in topic_suffixes
                ):
                    topic = core_topic

            return topic

    return None

# -----------------------------------
# Context-Aware Pronoun Resolution
# -----------------------------------

def resolve_pronoun(question, topic):

    history = get_context_history()

    # Find the most recent person
    # associated with the current topic
    person_reference = None

    if topic:

        for item in reversed(history):

            if (
                item["entity_type"] == "person"
                and item["topic"] == topic
            ):
                person_reference = item["entity"]
                break

    # If no person was found for the
    # current topic, fall back to
    # the most recent person
    if not person_reference:

        person_context = get_last_context("person")

        if person_context:
            person_reference = person_context["entity"]

    # If there is still no person,
    # leave the question unchanged
    if not person_reference:
        person_reference = topic

    if not person_reference:
        return question

    words = question.split()

    replacements = {
        "he": person_reference,
        "she": person_reference,
        "they": person_reference,
        "them": person_reference,

        "it": topic,
        "this": topic,
        "that": topic,
        "these": topic,
        "those": topic
    }

    resolved_words = []

    for word in words:

        clean_word = word.lower().strip("?!.,'\"")

        if clean_word in replacements:

            replacement = replacements[clean_word]

            if word[-1:] in "?!.,":

                replacement += word[-1]

            resolved_words.append(replacement)

        else:

            resolved_words.append(word)

    return " ".join(resolved_words)


# -----------------------------------
# Context-Aware Possessive Resolution
# -----------------------------------

def resolve_possessive(question, topic):

    history = get_context_history()

    # Find the most recent person
    # associated with the current topic
    person_reference = None

    if topic:

        for item in reversed(history):

            if (
                item["entity_type"] == "person"
                and item["topic"] == topic
            ):
                person_reference = item["entity"]
                break

    # Fallback to latest person
    if not person_reference:

        person_context = get_last_context("person")

        if person_context:
            person_reference = person_context["entity"]

    # If no person exists, use topic
    if not person_reference:

        person_reference = topic

    if not person_reference:

        return question

    words = question.split()

    replacements = {

        "its": f"{topic}'s",

        "their": f"{person_reference}'s",

        "his": f"{person_reference}'s",

        "her": f"{person_reference}'s"
    }

    resolved_words = []

    for word in words:

        clean_word = word.lower().strip(
            "?!.,'\""
        )

        if clean_word in replacements:

            replacement = replacements[clean_word]

            if word[-1:] in "?!.,":

                replacement += word[-1]

            resolved_words.append(replacement)

        else:

            resolved_words.append(word)

    return " ".join(resolved_words)


# -----------------------------------
# Resolve Follow-up Phrases
# -----------------------------------

def resolve_follow_up_phrase(question, topic):

    if not topic:
        return question

    question_lower = question.lower().strip()

    # --------------------------------
    # "What about Python?"
    # --------------------------------

    if question_lower.startswith("what about "):

        remainder = question[
            len("what about "):
        ].strip()

        return (
            f"What about {topic} "
            f"in relation to {remainder}"
        )

    # --------------------------------
    # "How about Python?"
    # --------------------------------

    if question_lower.startswith("how about "):

        remainder = question[
            len("how about "):
        ].strip()

        return (
            f"How about {topic} "
            f"in relation to {remainder}"
        )

    return question

# -----------------------------------
# Resolve Incomplete Follow-up
# -----------------------------------

def resolve_incomplete_follow_up(question, topic):

    if not topic:
        return question

    question_lower = question.lower().strip()

    # --------------------------------
    # Example requests
    # --------------------------------

    example_phrases = [
        "give me an example of",
        "give me another example of",
        "an example of",
        "example of",
        "give an example of",
        "show me an example of"
    ]

    for phrase in example_phrases:

        if question_lower.startswith(phrase):

            remainder = question[
                len(phrase):
            ].strip()

            # If the user already supplied
            # another subject, don't overwrite it
            if remainder:
                return question

            return f"Give me an example of {topic}"

    # --------------------------------
    # "Give me an example"
    # --------------------------------

    if question_lower in [
        "give me an example",
        "give me another example",
        "another example"
    ]:

        return f"Give me an example of {topic}"

    # --------------------------------
    # "More examples"
    # --------------------------------

    if question_lower in [
        "more examples",
        "give me more examples"
    ]:

        return f"Give me more examples of {topic}"

    return question

# -----------------------------------
# Resolve Context
# -----------------------------------

def resolve_context(question):

    if not question:
        return question

    # --------------------------------
    # Check whether question introduces
    # a new topic
    # --------------------------------

    extracted_topic = extract_topic(
        question
    )

    if extracted_topic:

        set_current_topic(
            extracted_topic
        )

        print(
            "New topic detected:",
            extracted_topic
        )

        return question

    # --------------------------------
    # Check follow-up
    # --------------------------------

    if detect_follow_up(question):

        current_topic = get_current_topic()

        if current_topic:
            # --------------------------------
            # Handle incomplete follow-ups
            # --------------------------------

            resolved = resolve_incomplete_follow_up(
                question,
                current_topic
            )

            # --------------------------------
            # Handle pronouns / entities
            # --------------------------------

            resolved = resolve_pronoun(
                resolved,
                current_topic
            )

            resolved = resolve_possessive(
                resolved,
                current_topic
            )

            resolved = resolve_follow_up_phrase(
                resolved,
                current_topic
            )

            print(
                "Original question:",
                question
            )

            print(
                "Current topic:",
                current_topic
            )

            print(
                "Resolved question:",
                resolved
            )

            return resolved

            resolved = resolve_possessive(
                resolved,
                current_topic
            )

            resolved = resolve_follow_up_phrase(
                resolved,
                current_topic
            )

            print(
                "Original question:",
                question
            )

            print(
                "Current topic:",
                current_topic
            )

            print(
                "Resolved question:",
                resolved
            )

            return resolved

    return question

# -----------------------------------
# Context-Aware Question Resolution
# -----------------------------------

def resolve_question_with_context(question):

    if not question:
        return question

    # First use our existing context resolution
    resolved = resolve_context(question)

    return resolved


# -----------------------------------
# Conversation State
# -----------------------------------

def get_entities():
    return conversation_state["entities"]

def get_conversation_state():

    return conversation_state


# -----------------------------------
# Clear Conversation
# -----------------------------------

def clear_conversation():

    conversation.clear()

    conversation_state["current_topic"] = None

    conversation_state["entities"].clear()

    conversation_state["previous_topics"].clear()

    conversation_state["last_entity"] = None

    conversation_state["context_history"].clear()


# -----------------------------------
# TEST
# -----------------------------------

if __name__ == "__main__":

    print("\n--- TEST 1 ---")

    question = "What is Python?"

    resolved = resolve_context(
        question
    )

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        "Python is a programming language."
    )

    question = "Who created it?"

    print(
        "Follow-up:",
        detect_follow_up(question)
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )


    print("\n--- TEST 2 ---")

    clear_conversation()

    question = "What is machine learning?"

    resolved = resolve_context(
        question
    )

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        "Machine learning allows computers to learn from data."
    )

    question = "What are its types?"

    print(
        "Follow-up:",
        detect_follow_up(question)
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )


    print("\n--- TEST 3 ---")

    clear_conversation()

    question = "What are neural networks?"

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    question = "How do they work?"

    print(
        "Follow-up:",
        detect_follow_up(question)
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )


    print("\n--- STATE ---")

    print(
        get_conversation_state()
    )

    print("\n--- TEST 4: TOPIC SWITCHING ---")

    clear_conversation()

    question = "What is Python?"

    resolved = resolve_context(question)

    print("Resolved:", resolved)

    question = "Who created it?"

    resolved = resolve_context(question)

    print("Resolved:", resolved)

    question = "What is machine learning?"

    resolved = resolve_context(question)

    print("Resolved:", resolved)

    question = "Who introduced it?"

    print(
        "Follow-up:",
        detect_follow_up(question)
    )

    resolved = resolve_context(question)

    print("Resolved:", resolved)

    print("\n--- FINAL STATE ---")

    print(get_conversation_state())

    print("\n--- TEST 5: ENTITY REFERENCE ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    question = "What was his background?"

    print(
        "Original:",
        question
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    print("\n--- ENTITY STATE ---")

    print(
        get_conversation_state()
    )

    print("\n--- TEST 6: PRONOUN ENTITY REFERENCE ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    question = "What did he do?"

    print(
        "Original:",
        question
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    print("\n--- TEST 7: MULTI ENTITY ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    track_entity(
        "technology",
        "Python"
    )

    track_entity(
        "technology",
        "Java"
    )

    track_entity(
        "person",
        "James Gosling"
    )

    print("\n--- ENTITY STATE ---")

    print(
        get_conversation_state()
    )

    print("\n--- TEST 8: MULTI ENTITY REFERENCE ---")

    question = "What did he do?"

    print(
        "Original:",
        question
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    print("\n--- TEST 9: CONTEXT HISTORY ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    set_current_topic("Java")

    track_entity(
        "person",
        "James Gosling"
    )

    print("\n--- CONTEXT HISTORY ---")

    print(
        get_context_history()
    )

    print("\n--- TEST 10: CONTEXT LOOKUP ---")

    last_person = get_last_context("person")

    print(
        "Last person context:",
        last_person
    )

    last_topic = get_last_context("topic")

    print(
        "Last topic context:",
        last_topic
    )

    print("\n--- TEST 11: TOPIC-AWARE PRONOUN ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    set_current_topic("Java")

    track_entity(
        "person",
        "James Gosling"
    )

    # Switch back to Python
    set_current_topic("Python")

    question = "What did he do?"

    print(
        "Original:",
        question
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    print("\n--- TEST 12: TOPIC-AWARE POSSESSIVE ---")

    clear_conversation()

    set_current_topic("Python")

    track_entity(
        "person",
        "Guido van Rossum"
    )

    set_current_topic("Java")

    track_entity(
        "person",
        "James Gosling"
    )

    # Switch back to Python
    set_current_topic("Python")

    question = "What was his background?"

    print(
        "Original:",
        question
    )

    resolved = resolve_context(
        question
    )

    print(
        "Resolved:",
        resolved
    )

    print("\n--- TEST 13: CONVERSATION HISTORY ---")

    clear_conversation()

    add_message(
        "user",
        "What is Python?"
    )

    add_message(
        "assistant",
        "Python is a programming language."
    )

    add_message(
        "user",
        "Who created it?"
    )

    add_message(
        "assistant",
        "Python was created by Guido van Rossum."
    )

    print("\nFormatted History:")

    print(
        format_conversation_history()
    )

    print("\nPython History:")

    print(
        search_conversation_history("python")
    )

    print("\n--- TEST 14: CONTEXT-AWARE QUESTION ---")

    clear_conversation()

    # Establish topic
    question = "What is Python?"

    resolve_context(question)

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        "Python is a programming language."
    )

    # Establish entity
    track_entity(
        "person",
        "Guido van Rossum"
    )

    question = "Who created it?"

    resolved = resolve_question_with_context(
        question
    )

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        "Guido van Rossum created Python."
    )

    print(
        "Resolved 1:",
        resolved
    )

    # Follow-up question
    question = "What was his background?"

    resolved = resolve_question_with_context(
        question
    )

    print(
        "Original 2:",
        question
    )

    print(
        "Resolved 2:",
        resolved
    )

    print("\n--- CONTEXT SUMMARY ---")

    print(
        get_context_summary()
    )