import ollama
from memory import (
    load_memory,
    get_all_memories,
    save_memory,
    remember_preference,
    recall_preference,
    remember_note,
    get_user_notes,
    get_user_name
)

from conversation import (
    add_message,
    get_recent_conversation,
    resolve_context,
    get_current_topic,
    get_entities
)

from rag import (
    initialize_rag,
    search_knowledge,
    filter_relevant_results,
    generate_general_answer
)
from tools import TOOLS

BROWSER_SEARCH_TEXT = ""

# -------------------------
# Known Creator Entities
# -------------------------

KNOWN_CREATORS = {
    "python": "Guido van Rossum",
    "java": "James Gosling"
}


def check_known_creator(question):
    question_lower = question.lower().strip()

    for technology, person in KNOWN_CREATORS.items():

        if technology in question_lower and (
                "who created" in question_lower
                or "who invented" in question_lower
                or "who developed" in question_lower
        ):
            from conversation import track_entity

            track_entity("person", person)

            return f"{technology.title()} was created by {person}."

    return None


# -------------------------
# Initialize RAG
# -------------------------

print("Initializing RAG...")

rag_index, rag_chunks = initialize_rag()

print("RAG ready!")

# -------------------------
# Assistant Personality
# -------------------------

SYSTEM_MESSAGE = """
You are Vectoria, a personal AI voice assistant.

CORE IDENTITY:
- Your name is Vectoria.
- You were created and developed by Yarasani Charlson.
- The developer's name must ALWAYS be written exactly as "Yarasani Charlson".
- If asked "Who built you?", "Who created you?", or "Who developed you?",
  answer that Yarasani Charlson created and developed you.
- If asked "Who are you?", identify yourself as Vectoria.
- If asked "Tell me about him", tell about his whole DEVLELOPER PROFILE.
- Never call yourself Charlson.

DEVELOPER PROFILE:
Yarasani Charlson is the creator and developer of Vectoria.
He has hands-on experience in Artificial Intelligence, Data Science,
Machine Learning, Python, Computer Vision and Embedded Systems.

His practical experience includes developing machine learning and
computer vision projects, working with robotics and embedded systems,
and serving as a Junior Robotics Trainer. He has experience building
technology projects that combine software, AI, and hardware.

EDUCATION:

Yarasani Charlson is currently pursuing a B.Tech in Computer Science Engineering (Data Science) at Hyderabad Institute of Technology and Management (HITAM), from 2025 to 2028.
Before his B.Tech, he completed a Polytechnic in Embedded Systems at the Government Institute of Electronics, from 2022 to 2025.


IMPORTANT:
- Use the developer profile ONLY when the user specifically asks about
  Yarasani Charlson, his background, his experience, or his role as the developer.
- If the user only asks "Who built you?", give the creator/developer
  identity and do not give the full developer profile.
- Do not invent additional information about Yarasani Charlson.
- Do not provide college details, marks, contact information, or other
  personal information unless explicitly provided for that question.
- Never assume that Yarasani Charlson created, invented, developed,
  founded, or contributed to a technology, programming language,
  company, person, or historical subject unless this is explicitly
  stated in the developer profile.
- The developer profile describes the creator of Vectoria only.
- Do not use information about Yarasani Charlson to answer questions
  about unrelated technologies or their creators.
- When answering questions about the creator of another technology,
  rely on the actual subject and conversation context, not the
  Vectoria developer identity.

CONVERSATION:
- Be friendly and natural.
- Keep responses concise and natural for voice interaction.
- Give more detail when the user asks for an explanation or detailed answer.
- Do not unnecessarily repeat information.
- Use previous conversation context when relevant.

MEMORY:
- Use stored memories when relevant.
- Do not claim to remember something that is not available.

Response style:
- Give a complete answer to the user's question.
- Keep the answer concise and suitable for voice interaction.
- For simple factual questions, answer in 1-3 sentences.
- For explanation questions, give the definition and 2-4 key points.
- Do not use analogies, stories, or hypothetical examples unless specifically requested.
- Do not unnecessarily expand the answer.
- Avoid long numbered lists.
- Do not repeat the same idea in different words.
- If the question asks about a person's background, provide the most relevant background details in 2-4 sentences.
- Do not invent specific facts, dates, organizations, titles, or biographical details.
- If uncertain about a specific fact, say that you are uncertain rather than guessing.
- Always finish the answer naturally and never stop in the middle of a sentence or list.
- Keep general answers concise and suitable for voice conversation.
- Normally answer in 1–3 short sentences.
- Do not use numbered lists or bullet points unless the user explicitly asks for them.
- Do not provide extra details unless the user asks for more.

"""


# -------------------------
# Generic Memory Lookup
# -------------------------

def check_memory(question, memory):
    question_lower = question.lower().strip()

    preferences = memory.get("preferences", {})
    user_notes = memory.get("user_notes", [])

    # --------------------------------
    # Favourite / Favorite questions
    # --------------------------------

    if (
            "favourite " in question_lower
            or "favorite " in question_lower
    ):

        marker = (
            "favourite "
            if "favourite " in question_lower
            else "favorite "
        )

        category = question_lower.split(
            marker,
            1
        )[1]

        category = category.rstrip("?").strip()

        category = category.replace("who is ", "")
        category = category.replace("what is ", "")
        category = category.replace("what are ", "")
        category = category.strip()

        # --------------------------------
        # Direct lookup
        # --------------------------------

        value = preferences.get(category)

        if value:
            return (
                f"Your favourite {category} is "
                f"{str(value).title()}."
            )

        # --------------------------------
        # Alias matching
        # --------------------------------

        aliases = {
            "artist": [
                "artist",
                "singer",
                "entertainer",
                "artist_who"
            ],
            "singer": [
                "singer",
                "artist",
                "entertainer",
                "artist_who"
            ],
            "movie": [
                "movie",
                "film"
            ],
            "programming language": [
                "programming_language",
                "programming language",
                "language"
            ],
            "instrument": [
                "instrument"
            ],
            "food": [
                "food"
            ],
            "subject": [
                "subject"
            ],
            "hobby": [
                "hobby"
            ]
        }

        possible_keys = aliases.get(
            category,
            [category]
        )

        for key in possible_keys:

            value = preferences.get(key)

            if value:
                return (
                    f"Your favourite {category} is "
                    f"{str(value).title()}."
                )

        # --------------------------------
        # Search user notes
        # --------------------------------

        for note in user_notes:

            note_lower = note.lower()

            if (
                    f"favourite {category}" in note_lower
                    or f"favorite {category}" in note_lower
            ):

                if " is " in note:
                    value = note.split(
                        " is ",
                        1
                    )[1].strip()

                    return (
                        f"Your favourite {category} is "
                        f"{value.title()}."
                    )

    return None


# -------------------------
# Personal Profile Router
# -------------------------

def check_personal_profile(question):
    q = question.lower().strip()

    # -------------------------
    # User identity
    # -------------------------

    identity_questions = [
        "what is my name",
        "what's my name",
        "who am i",
        "who am i?",
        "what is the user's name",
        "what's the user's name",
        "what is charlson's name",
        "who is charlson"
    ]

    if any(
            phrase in q
            for phrase in identity_questions
    ):
        return "Your name is Yarasani Charlson."

    # -------------------------
    # Education - current
    # -------------------------

    current_education = [
        "what am i studying",
        "what i'm studying",
        "what i am studying",
        "where am i studying",
        "where i'm studying",
        "where i am studying",
        "what are you studying",
        "what you're studying",
        "what you are studying",
        "where are you studying",
        "where you're studying",
        "where you are studying",
        "what is charlson studying",
        "what is yarasani charlson studying",
        "where is charlson studying",
        "where is yarasani charlson studying"
    ]

    if any(phrase in q for phrase in current_education):

        # Questions referring to the user
        if any(phrase in q for phrase in [
            "where am i",
            "what am i",
            "where i'm",
            "what i'm",
            "where i am",
            "what i am",
            "my "
        ]):
            return (
                "You are currently pursuing a B.Tech in Computer Science "
                "Engineering (Data Science) at Hyderabad Institute of "
                "Technology and Management (HITAM)."
            )

        # Questions referring to Charlson
        return (
            "Yarasani Charlson is currently pursuing a B.Tech in Computer "
            "Science Engineering (Data Science) at Hyderabad Institute of "
            "Technology and Management (HITAM)."
        )

    # -------------------------
    # Previous education
    # -------------------------

    previous_education = [
        "where did i study before",
        "what did i study before",
        "where did you study before",
        "what did you study before",
        "where did charlson study before",
        "what did charlson study before",
        "where did yarasani charlson study before",
        "what did yarasani charlson study before"
    ]

    if any(phrase in q for phrase in previous_education):
        return (
            "Before your B.Tech, you completed a Polytechnic in "
            "Embedded Systems at the Government Institute of Electronics."
        )

    # -------------------------
    # Educational qualifications
    # -------------------------

    qualification_questions = [
        "what are my educational qualifications",
        "what are your educational qualifications",
        "what are my qualifications",
        "what are your qualifications",
        "what did i study",
        "what did you study",
        "what is my education",
        "what is your education"
    ]

    if any(phrase in q for phrase in qualification_questions):
        return (
            "You are currently pursuing a B.Tech in Computer Science "
            "Engineering (Data Science) at Hyderabad Institute of "
            "Technology and Management (HITAM). Before that, you "
            "completed a Polytechnic in Embedded Systems at the "
            "Government Institute of Electronics."
        )

    third_person_qualification_questions = [
        "what are charlson's educational qualifications",
        "what are yarasani charlson's educational qualifications",
        "what are charlson's qualifications",
        "what are yarasani charlson's qualifications",
        "what did charlson study",
        "what did he study",
        "what did he do",
        "what did yarasani charlson study",
        "what is charlson's education",
        "what is yarasani charlson's education"
    ]

    if any(phrase in q for phrase in third_person_qualification_questions):
        return (
            "Yarasani Charlson is currently pursuing a B.Tech in Computer "
            "Science Engineering (Data Science) at Hyderabad Institute of "
            "Technology and Management (HITAM). Before that, he completed "
            "a Polytechnic in Embedded Systems at the Government Institute "
            "of Electronics."
        )

    return None


def route_question(question):
    results = search_knowledge(
        question,
        rag_index,
        rag_chunks,
        top_k=3
    )

    if not results:
        print("No RAG results found.")
        return "normal", results

    top_result = results[0]

    top_similarity = top_result["similarity"]
    top_adjusted = top_result["adjusted_similarity"]

    if len(results) > 1:
        second_similarity = results[1]["similarity"]
        second_adjusted = results[1]["adjusted_similarity"]
    else:
        second_similarity = 0.0
        second_adjusted = 0.0

    similarity_gap = top_adjusted - second_adjusted

    print("Top similarity:", top_similarity)
    print("Top adjusted similarity:", top_adjusted)

    print("Second similarity:", second_similarity)
    print("Second adjusted similarity:", second_adjusted)

    print("Adjusted similarity gap:", similarity_gap)

    # ---------------------------------
    # Very weak semantic match
    # ---------------------------------

    if top_similarity < 0.30:
        print("RAG confidence too low.")
        print("RAG search skipped.")
        return "normal", results

    # ---------------------------------
    # Strong semantic match
    # ---------------------------------

    if top_similarity >= 0.75:
        return "rag", results

    # ---------------------------------
    # Good semantic match
    # ---------------------------------

    if top_similarity >= 0.50:
        return "rag", results

    # ---------------------------------
    # Explicit topic match + adjusted score
    # ---------------------------------

    topic = top_result.get("topic", "").lower().strip()

    question_lower = question.lower()

    topic_match = (
            topic
            and topic != "statistics"
            and topic in question_lower
    )

    print("RAG topic:", topic)
    print("Topic match:", topic_match)

    if topic_match and top_adjusted >= 0.50:
        print("Explicit topic match detected.")
        return "rag", results

    # ---------------------------------
    # Uncertain semantic match
    # ---------------------------------

    if top_similarity >= 0.30 and similarity_gap >= 0.05:
        print("RAG relevance uncertain.")
        return "uncertain", results

    # ---------------------------------
    # General AI
    # ---------------------------------

    return "normal", results


# -------------------------
# Automatic Memory Detection
# -------------------------

def detect_memory(question):
    question_lower = question.lower().strip()

    # -------------------------
    # Favourite / Favorite
    # -------------------------

    if (
            question_lower.startswith("my favourite ")
            or question_lower.startswith("my favorite ")
    ):

        if " is " in question_lower:

            parts = question_lower.split(
                " is ",
                1
            )

            category = parts[0]

            value = parts[1].strip()

            category = (
                category
                .replace("my favourite ", "")
                .replace("my favorite ", "")
                .strip()
            )

            memory = load_memory()

            if "preferences" not in memory:
                memory["preferences"] = {}

            key = category.replace(" ", "_")

            remember_preference(
                key,
                value
            )

            print(
                "Structured memory saved:",
                key,
                "=",
                value
            )

            return True

    return False


# -------------------------
# Generic Memory Write Router
# -------------------------

def detect_memory_write(question):
    question_lower = question.lower().strip()

    # Only process "remember..." statements
    if not (
            question_lower.startswith("remember ")
            or question_lower.startswith("remember that ")
    ):
        return False

    # Remove "remember" / "remember that"
    if question_lower.startswith("remember that "):

        text = question_lower[len("remember that "):].strip()

    else:

        text = question_lower[len("remember "):].strip()

    # Remove punctuation
    text = text.rstrip(".!?").strip()

    value = None
    category = None

    # --------------------------------
    # Pattern 1:
    # Michael Jackson is my favourite singer
    # Billie Jean is my favourite song
    # --------------------------------

    marker = " is my favourite "

    if marker in text:

        value, category = text.split(
            marker,
            1
        )

    else:

        marker = " is my favorite "

        if marker in text:
            value, category = text.split(
                marker,
                1
            )

    # --------------------------------
    # Pattern 2:
    # my favourite singer is Michael Jackson
    # my favourite song is Billie Jean
    # my favourite subject is data science
    # --------------------------------

    if category is None:

        # --------------------------------
        # Pattern:
        # my favourite subject is data science
        # my favourite singer is Michael Jackson
        # my favourite song is Billie Jean
        # --------------------------------

        if text.startswith("my favourite "):

            remainder = text[len("my favourite "):].strip()

        elif text.startswith("my favorite "):

            remainder = text[len("my favorite "):].strip()

        else:

            remainder = None

        if remainder and " is " in remainder:

            category, value = remainder.split(
                " is ",
                1
            )

        else:

            marker = "my favorite "

            if marker in text:

                category, value = text.split(
                    marker,
                    1
                )

                if " is " in value:
                    value = value.split(
                        " is ",
                        1
                    )[1]

    # --------------------------------
    # Validate
    # --------------------------------

    if category is None or value is None:
        return False

    category = category.strip()
    value = value.strip()

    if not category or not value:
        return False

    # --------------------------------
    # Save automatically
    # --------------------------------

    key = category.replace(" ", "_")

    remember_preference(
        key,
        value
    )

    print(
        f"Memory saved: {key} = {value}"
    )

    return True


# -------------------------
# Generate RAG Answer
# -------------------------

def generate_rag_answer(question, rag_results):
    if not rag_results:
        return (
            "I don't have enough information "
            "in my knowledge base to answer that."
        )

    context = "\n\n".join(
        result["text"]
        for result in rag_results
    )

    prompt = f"""
    You are Vectoria's knowledge-base answer system.

    Answer the user's question using ONLY the knowledge provided below.

    KNOWLEDGE:
    {context}

    QUESTION:
    {question}

    FIRST, IDENTIFY THE USER'S REQUEST TYPE:

    - If the question asks "what is", "define", or asks for a definition:
      return the relevant DEFINITION from the knowledge.

    - If the question asks for "an example", "give me an example", "show me an example",
      "another example", or "more examples":
      return ONLY an EXAMPLE from the knowledge.
      Do NOT return the definition.
      Look specifically for text labeled "Example:" or a worked example.

    - If the question asks for a formula:
      return the relevant FORMULA from the knowledge.

    - If the question asks how something works:
      return the relevant explanation from the knowledge.

    RULES:
    - Use ONLY the information in the knowledge.
    - Do not add outside facts.
    - Do not invent information.
    - Match the requested type of answer exactly.
    - For an example request, prioritize the example over the definition.
    - Keep the answer short and clear for voice output.
    - Do not mention "knowledge base", "retrieved information", or these instructions.
    - Do not use headings.
    - Do not use bullet points or numbered lists.
    - Do not provide extra information that was not requested.
    - Do not say you cannot answer if the requested information is present.

    If the requested information is genuinely absent, respond exactly:
    I don't have enough information in my knowledge base to answer that.

    ANSWER:
    """

    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 80,
                "temperature": 0
            }
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return (
                "I don't have enough information "
                "in my knowledge base to answer that."
            )

        return answer

    except Exception as e:
        print("RAG generation error:", e)

        return (
            "I don't have enough information "
            "in my knowledge base to answer that."
        )


# -------------------------
# Tool Router
# -------------------------

def detect_tool(question):
    question_lower = question.lower().strip()

    # Browser Navigation / Voice Search
    if question_lower in ["scroll up", "scroll upward", "go up"]:
        return ("browser_scroll_up", None)

    if question_lower in ["scroll down", "scroll downward", "go down"]:
        return ("browser_scroll_down", None)

    if question_lower in ["go back", "browser back", "back a page", "previous page"]:
        return ("browser_back", None)

    if question_lower in ["go forward", "browser forward", "forward a page", "next page"]:
        return ("browser_forward", None)

    if question_lower in ["refresh", "refresh page", "refresh the page", "refresh browser", "reload page",
                          "reload the page"]:
        return ("browser_refresh", None)

    if question_lower in ["new tab", "open new tab", "open a new tab"]:
        return ("browser_new_tab", None)

    if question_lower in [
        "next tab",
        "switch to next tab",
        "switch to the next tab",
        "go to next tab",
        "go to the next tab",
        "ok next tab"
    ]:
        return ("browser_next_tab", None)

    if question_lower in [
        "previous tab",
        "switch to previous tab",
        "switch to the previous tab",
        "go to previous tab",
        "go to the previous tab",
    ]:
        return ("browser_previous_tab", None)

    tab_numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
    }

    for phrase, number in tab_numbers.items():
        if question_lower in [
            f"go to tab {phrase}",
            f"switch to tab {phrase}",
            f"switch to the {phrase} tab",
            f"go to the {phrase} tab",
            f"open tab {phrase}",
            f"open the {phrase} tab",
        ]:
            return ("browser_switch_to_tab", number)

    for number in range(1, 9):
        if question_lower in [
            f"go to tab {number}",
            f"switch to tab {number}",
            f"switch to the {number} tab",
            f"go to the {number} tab",
            f"open tab {number}",
            f"open the {number} tab",
        ]:
            return ("browser_switch_to_tab", number)

        if question_lower in ["close tab", "close this tab", "close the tab"]:
            return ("browser_close_tab", None)

        if question_lower in ["focus search bar", "focus the search bar", "open search bar", "open the search bar"]:
            return ("browser_focus_search", None)

        if question_lower in ["backspace", "press backspace", "delete previous character",
                              "delete the previous character"]:
            return ("browser_backspace", None)

        if question_lower in ["delete last word", "delete the last word", "delete previous word",
                              "delete the previous word"]:
            return ("browser_delete_word", None)

        if question_lower in ["clear search", "clear the search", "clear search bar", "clear the search bar"]:
            return ("browser_clear_search", None)

        if question_lower in ["search", "search now", "submit search", "press enter", "press return"]:
            return ("browser_search", None)

        for prefix in ["search for ", "search ", "look for ", "look up ", "type ", "type in ", "enter ", "write "]:
            if question_lower.startswith(prefix):
                text = question[len(prefix):].strip()
                if text:
                    return ("browser_type_text", text)

        if "skip forward" in question_lower or "skip ahead" in question_lower:
            return ("browser_skip_forward", None)

        if "skip backward" in question_lower or "skip back" in question_lower:
            return ("browser_skip_backward", None)

        # YouTube Video Selection
        youtube_video_numbers = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5
        }

        for word, number in youtube_video_numbers.items():
            if (
                    f"play the {word} video" in question_lower
                    or f"play {word} video" in question_lower
                    or f"select the {word} video" in question_lower
                    or f"select {word} video" in question_lower
                    or f"open the {word} video" in question_lower
                    or f"open {word} video" in question_lower
            ):
                return ("browser_select_youtube_video", number)

        question_lower = question.lower().strip()

        # -------------------------
        # Unit Converter
        # -------------------------

        conversion_keywords = [
            "convert",
            "how many",
            "how much",
            "conversion"
        ]

        units = [
            "meter", "meters", "m",
            "kilometer", "kilometers", "km",
            "centimeter", "centimeters", "cm",
            "millimeter", "millimeters", "mm",
            "mile", "miles",
            "yard", "yards",
            "foot", "feet",
            "inch", "inches",

            "kilogram", "kilograms", "kg",
            "gram", "grams", "g",
            "pound", "pounds", "lb", "lbs",
            "ounce", "ounces", "oz",

            "celsius", "fahrenheit", "kelvin"
        ]

        has_conversion_keyword = any(
            keyword in question_lower
            for keyword in conversion_keywords
        )

        has_unit = any(
            unit in question_lower
            for unit in units
        )

        if has_conversion_keyword and has_unit:

            import re

            pattern = (
                r"(-?\d+(?:\.\d+)?)\s*"
                r"([a-zA-Z]+)\s+"
                r"(?:to|into|in)\s+"
                r"([a-zA-Z]+)"
            )

            match = re.search(pattern, question_lower)

            if match:
                value = float(match.group(1))
                from_unit = match.group(2)
                to_unit = match.group(3)

                return (
                    "unit_converter",
                    (value, from_unit, to_unit)
                )

        # -------------------------
        # Timer Tool
        # -------------------------

        timer_keywords = [
            "set a timer",
            "start a timer",
            "timer for",
            "set timer"
        ]

        if any(
                keyword in question_lower
                for keyword in timer_keywords
        ):

            import re

            match = re.search(
                r"(?:timer\s+for|timer)\s+(\d+(?:\.\d+)?)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)",
                question_lower
            )

            if match:

                value = float(match.group(1))
                unit = match.group(2)

                if unit.startswith("second") or unit.startswith("sec"):
                    seconds = value

                elif unit.startswith("minute") or unit.startswith("min"):
                    seconds = value * 60

                elif unit.startswith("hour") or unit.startswith("hr"):
                    seconds = value * 3600

                else:
                    return None

                return (
                    "timer",
                    int(seconds)
                )

        # -------------------------
        # Reminder Tool
        # -------------------------

        reminder_keywords = [
            "remind me",
            "set a reminder",
            "reminder for"
        ]

        if any(
                keyword in question_lower
                for keyword in reminder_keywords
        ):

            import re

            match = re.search(
                r"(?:remind me|set a reminder|reminder)\s+(?:in|for)\s+"
                r"(\d+(?:\.\d+)?)\s*"
                r"(seconds?|secs?|minutes?|mins?|hours?|hrs?)"
                r"(?:\s+to\s+|\s+about\s+|\s*:\s*)(.+)",
                question_lower
            )

            if match:

                value = float(match.group(1))
                unit = match.group(2)
                message = match.group(3).strip()

                if unit.startswith("second") or unit.startswith("sec"):
                    seconds = value

                elif unit.startswith("minute") or unit.startswith("min"):
                    seconds = value * 60

                elif unit.startswith("hour") or unit.startswith("hr"):
                    seconds = value * 3600

                else:
                    return None

                return (
                    "reminder",
                    (int(seconds), message)
                )

        # -------------------------
        # Weather
        # -------------------------

        weather_keywords = [
            "weather",
            "temperature",
            "forecast"
        ]

        if any(
                keyword in question_lower
                for keyword in weather_keywords
        ):

            import re

            match = re.search(
                r"(?:weather|temperature|forecast).*?\b(?:in|at|for)\s+([a-zA-Z\s]+)",
                question_lower
            )

            if match:
                city = match.group(1).strip()

                return (
                    "weather",
                    city
                )

        # -------------------------
        # Computer Control
        # -------------------------

        import re

        # Screenshot
        if any(phrase in question_lower for phrase in [
            "take a screenshot",
            "take screenshot",
            "capture the screen",
            "capture screen",
            "screenshot"
        ]):
            return ("take_screenshot", None)

        # Lock computer
        if any(phrase in question_lower for phrase in [
            "lock my computer",
            "lock the computer",
            "lock my pc",
            "lock the pc",
            "lock computer"
        ]):
            return ("lock_computer", None)

        # Create a folder
        create_match = re.search(
            r"(?:create|make)\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called|named)\s+(.+)$",
            question_lower
        )
        if create_match:
            return ("create_folder", create_match.group(1).strip().rstrip("?."))

        # Search for a file/folder
        search_match = re.search(
            r"(?:search|find|look)\s+(?:for\s+)?(?:my\s+)?(?:file|folder|document|project)?\s*(?:called|named)?\s*(.+)$",
            question_lower
        )
        if search_match and any(word in question_lower for word in [
            "search", "find", "look for"
        ]):
            query = search_match.group(1).strip().rstrip("?.")
            if query:
                return ("search_files", query)

        # Common Windows folders
        common_folders = [
            "downloads",
            "documents",
            "desktop",
            "pictures",
            "music",
            "videos"
        ]

        if any(keyword in question_lower for keyword in ["open", "go to", "show"]):
            for folder in common_folders:
                if folder in question_lower:
                    return ("open_path", folder)

        # Open a specific file/folder/project by name. This is deliberately
        # restricted to explicit file/folder/project wording so normal app/site
        # launch commands keep their existing routing.
        if any(word in question_lower for word in ["file", "folder", "project", "document"]):
            open_match = re.search(
                r"(?:open|launch|start|show)\s+(?:the\s+)?(.+)$",
                question_lower
            )
            if open_match:
                target = open_match.group(1).strip().rstrip("?.")
                if target.startswith("the "):
                    target = target[4:].strip()
                for prefix in ["file ", "folder ", "project ", "document "]:
                    if target.startswith(prefix):
                        target = target[len(prefix):].strip()
                for suffix in [" file", " folder", " project", " document"]:
                    if target.endswith(suffix):
                        target = target[:-len(suffix)].strip()
                if target:
                    return ("open_path", target)

        # -------------------------
        # Window Control
        # -------------------------

        window_actions = {
            "minimize": "window_minimize",
            "minimise": "window_minimize",
            "maximize": "window_maximize",
            "maximise": "window_maximize",
            "switch to": "window_activate",
            "activate": "window_activate",
            "focus": "window_activate",
            "close": "window_close"
        }

        window_targets = [
            "google chrome",
            "chrome",
            "visual studio code",
            "vscode",
            "notepad",
            "calculator",
            "calc",
            "paint",
            "wordpad",
            "file explorer",
            "explorer",
            "command prompt",
            "cmd",
            "powershell",
            "settings"
        ]

        for action, tool_name in window_actions.items():

            if action in question_lower:

                remaining = question_lower.replace(action, "").strip()

                for target in sorted(window_targets, key=len, reverse=True):

                    if target in remaining:
                        return (tool_name, target)

        # -------------------------
        # Application Launcher
        # -------------------------

        application_keywords = [
            "open",
            "launch",
            "start",
            "run"
        ]

        applications = [
            "google chrome",
            "chrome",
            "notepad",
            "calculator",
            "calc",
            "paint",
            "wordpad",
            "file explorer",
            "explorer",
            "command prompt",
            "cmd",
            "powershell",
            "visual studio code",
            "vscode"
        ]

        has_application_keyword = any(
            keyword in question_lower
            for keyword in application_keywords
        )

        if has_application_keyword:

            # Check longer names first
            for application in sorted(
                    applications,
                    key=len,
                    reverse=True
            ):

                if application in question_lower:
                    return (
                        "application_launcher",
                        application
                    )

        # -------------------------
        # Calculator
        # -------------------------

        calculator_keywords = [
            "+",
            "-",
            "*",
            "/",
            "%",
            "plus",
            "minus",
            "times",
            "multiply",
            "multiplied",
            "divide",
            "divided"
        ]

        if any(
                keyword in question_lower
                for keyword in calculator_keywords
        ):

            expression = question_lower

            # Remove common question phrases
            for phrase in [
                "what is",
                "calculate",
                "compute",
                "solve"
            ]:
                expression = expression.replace(
                    phrase,
                    ""
                )

            # Convert spoken operators
            expression = expression.replace(
                "multiplied by",
                "*"
            )

            expression = expression.replace(
                "multiply by",
                "*"
            )

            expression = expression.replace(
                "divided by",
                "/"
            )

            expression = expression.replace(
                "times",
                "*"
            )

            expression = expression.replace(
                "plus",
                "+"
            )

            expression = expression.replace(
                "minus",
                "-"
            )

            expression = expression.replace(
                "divide",
                "/"
            )

            # Handle standalone x as multiplication
            expression = expression.replace(
                " x ",
                " * "
            )

            expression = expression.replace(
                "?",
                ""
            ).strip()

            return "calculator", expression

        # -------------------------
        # Time
        # -------------------------

        if "time" in question:
            return ("time", None)

        # -------------------------
        # Date
        # -------------------------

        if "date" in question or "today's date" in question:
            return ("date", None)

        # -------------------------
        # Day
        # -------------------------

        if "day" in question:
            return ("day", None)

        # -------------------------
        # Year
        # -------------------------

        if "year" in question:
            return ("year", None)
        # -------------------------
        # Application Launcher
        # -------------------------

        application_keywords = [
            "open",
            "launch",
            "start",
            "run"
        ]

        applications = [
            "google chrome",
            "chrome",
            "notepad",
            "calculator",
            "calc",
            "paint",
            "wordpad",
            "file explorer",
            "explorer",
            "command prompt",
            "cmd",
            "powershell",
            "visual studio code",
            "vscode"
        ]

        has_application_keyword = any(
            keyword in question
            for keyword in application_keywords
        )

        if has_application_keyword:

            for application in sorted(
                    applications,
                    key=len,
                    reverse=True
            ):

                if application in question:
                    return (
                        "application_launcher",
                        application
                    )

        # -------------------------
        # Media Control
        # -------------------------

        if "play" in question or "pause" in question:
            if "music" in question or "song" in question or "media" in question:
                return ("media_play_pause", None)

        if "next" in question:
            if "song" in question or "track" in question or "music" in question:
                return ("media_next", None)

        if "previous" in question or "prev" in question:
            if "song" in question or "track" in question or "music" in question:
                return ("media_previous", None)

        # -------------------------
        # Website Launcher
        # -------------------------

        website_keywords = [
            "open",
            "launch",
            "start"
        ]

        websites = [
            "google drive",
            "youtube",
            "chatgpt",
            "github",
            "gmail",
            "linkedin",
            "instagram",
            "facebook",
            "whatsapp",
            "google"
        ]

        has_website_keyword = any(
            keyword in question
            for keyword in website_keywords
        )

        if has_website_keyword:

            for website in sorted(
                    websites,
                    key=len,
                    reverse=True
            ):

                if website in question:
                    return (
                        "website_launcher",
                        website
                    )

        # -------------------------
        # Volume Control
        # -------------------------

        if "increase" in question or "turn up" in question or "raise" in question:
            if "volume" in question or "sound" in question:
                return ("volume_up", None)

        if "decrease" in question or "turn down" in question or "lower" in question:
            if "volume" in question or "sound" in question:
                return ("volume_down", None)

        if "unmute" in question:
            return ("volume_unmute", None)

        if "mute" in question:
            return ("volume_mute", None)

        import re

        volume_match = re.search(
            r"(?:set|change|adjust)\s+(?:the\s+)?volume\s+(?:to\s+)?(\d+)\s*(?:percent|%)?",
            question
        )

        if volume_match:
            level = int(volume_match.group(1))
            return ("volume_set", level)

        # Spoken numbers
        spoken_numbers = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "twenty": 20,
            "thirty": 30,
            "forty": 40,
            "fifty": 50,
            "sixty": 60,
            "seventy": 70,
            "eighty": 80,
            "ninety": 90,
            "one hundred": 100
        }

        spoken_volume_match = re.search(
            r"(?:set|change|adjust)\s+(?:the\s+)?volume\s+(?:to\s+)?(.+?)(?:\s+percent|\s+%)?$",
            question
        )

        if spoken_volume_match:
            spoken_level = spoken_volume_match.group(1).strip()

            if spoken_level in spoken_numbers:
                return ("volume_set", spoken_numbers[spoken_level])

        # -------------------------
        # System Information
        # -------------------------

        system_info_phrases = [
            "system information",
            "system info",
            "system usage",
            "system status",
            "computer information",
            "computer info",
            "computer status",
            "pc information",
            "pc info",
            "cpu usage",
            "cpu utilization",
            "ram usage",
            "ram utilization",
            "memory usage",
            "memory utilization",
            "disk usage",
            "disk space",
            "storage space",
        ]

        if any(phrase in question_lower for phrase in system_info_phrases):
            return ("system_info", None)

        # Natural RAM/CPU/Disk questions
        if "ram" in question_lower or "memory" in question_lower:
            if any(word in question_lower for word in ["using", "used", "usage", "much", "available", "left"]):
                return ("system_info", None)

        if "cpu" in question_lower:
            if any(word in question_lower for word in ["using", "used", "usage", "much", "utilization"]):
                return ("system_info", None)

        if "disk" in question_lower or "storage" in question_lower:
            if any(word in question_lower for word in ["using", "used", "usage", "space", "available", "left"]):
                return ("system_info", None)

        return None, None

    return ("browser_previous_tab", None)


# -------------------------
# LLM Tool Selection
# -------------------------

def select_tool(question):
    prompt = f"""
Classify the user question into exactly ONE category.

QUESTION:
{question}

Categories:

CALCULATOR = arithmetic or mathematical calculation
TIME = asks for the current time
NONE = everything else

Examples:

Question: What is 25 * 48?
Answer: CALCULATOR

Question: Calculate 100 / 5
Answer: CALCULATOR

Question: What time is it?
Answer: TIME

Question: Tell me the current time
Answer: TIME

Question: What is the mean?
Answer: NONE

Question: Who is the president?
Answer: NONE

Return ONLY:
CALCULATOR
TIME
or
NONE
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
            "num_predict": 5
        }
    )

    result = (
        response["message"]["content"]
        .strip()
        .upper()
    )

    if "CALCULATOR" in result:
        return "calculator"

    if "TIME" in result:
        return "time"

    return "none"


# -------------------------
# Execute Tool
# -------------------------

def execute_tool(tool_name, tool_input=None):
    global BROWSER_SEARCH_TEXT

    if tool_name == "browser_type_text":
        BROWSER_SEARCH_TEXT = str(tool_input)
        return TOOLS[tool_name]["function"](tool_input)

    if tool_name == "browser_backspace":
        result = TOOLS[tool_name]["function"]()
        BROWSER_SEARCH_TEXT = BROWSER_SEARCH_TEXT[:-1]
        return result

    if tool_name == "browser_delete_word":
        result = TOOLS[tool_name]["function"]()
        words = BROWSER_SEARCH_TEXT.rstrip().split()
        BROWSER_SEARCH_TEXT = " ".join(words[:-1]) if words else ""
        return result

    if tool_name == "browser_clear_search":
        result = TOOLS[tool_name]["function"]()
        BROWSER_SEARCH_TEXT = ""
        return result

    if tool_name not in TOOLS:
        return None

    tool = TOOLS[tool_name]
    function = tool["function"]

    if tool_name == "unit_converter":
        value, from_unit, to_unit = tool_input

        return function(
            value,
            from_unit,
            to_unit
        )

    if tool_name == "reminder":
        seconds, message = tool_input
        return function(seconds, message)

    if tool_name == "volume_set":
        return function(tool_input)

    if tool["requires_input"]:
        return function(tool_input)

    return function()


# -------------------------
# Track Known Person Entity
# -------------------------

def track_known_entity(question):
    question_lower = question.lower()

    for technology, person in KNOWN_CREATORS.items():

        if (
                technology in question_lower
                and (
                "who created" in question_lower
                or "who invented" in question_lower
                or "who developed" in question_lower
                or "who founded" in question_lower
        )
        ):
            from conversation import track_entity

            track_entity(
                "person",
                person
            )

            print(
                "Known person entity tracked:",
                person
            )

            return person

    return None


# -------------------------
# Ask AI
# -------------------------

def ask_ai(question):
    print("Thinking...")

    # -------------------------
    # Detect Memory Write
    # -------------------------

    memory_saved = detect_memory_write(question)

    if memory_saved:
        answer = "I'll remember that."

        add_message(
            "user",
            question
        )

        add_message(
            "assistant",
            answer
        )

        return answer

    # -------------------------
    # Existing Automatic Memory
    # -------------------------

    detect_memory(question)

    # -------------------------
    # Load long-term memory
    # -------------------------

    memory = load_memory()

    # -------------------------
    # Direct Memory Lookup
    # -------------------------

    direct_answer = check_memory(
        question,
        memory
    )

    if direct_answer:
        print("Direct memory lookup used.")

        add_message(
            "user",
            question
        )

        add_message(
            "assistant",
            direct_answer
        )

        return direct_answer

    search_question = resolve_context(question)

    known_creator_answer = check_known_creator(search_question)

    if known_creator_answer:
        add_message("user", question)
        add_message("assistant", known_creator_answer)

        print("Known creator answer.")
        return known_creator_answer

    # -------------------------
    # Track known entities
    # -------------------------

    track_known_entity(search_question)

    print("Current topic:", get_current_topic())
    print("Entities:", get_entities())

    # -------------------------
    # Personal Profile Lookup
    # -------------------------

    profile_answer = check_personal_profile(
        question
    )

    if profile_answer:
        print("Personal profile lookup used.")

        add_message(
            "user",
            question
        )

        add_message(
            "assistant",
            profile_answer
        )

        return profile_answer

    # -------------------------
    # Check for Tools
    # -------------------------

    tool, tool_input = detect_tool(
        search_question
    )

    if tool:

        tool_result = execute_tool(
            tool,
            tool_input
        )

        if tool == "calculator":
            answer = f"The answer is {tool_result}."

        elif tool == "time":
            answer = f"The current time is {tool_result}."

        elif tool == "date":
            answer = f"Today's date is {tool_result}."

        elif tool == "day":
            answer = f"Today is {tool_result}."

        elif tool == "year":
            answer = f"The current year is {tool_result}."

        elif tool == "unit_converter":

            value, from_unit, to_unit = tool_input

            answer = (
                f"{value:g} {from_unit} is approximately "
                f"{tool_result:.2f} {to_unit}."
            )

        elif tool == "weather":

            answer = (
                f"In {tool_result['city']}, "
                f"it's {tool_result['temperature']} degrees Celsius, "
                f"feels like {tool_result['feels_like']} degrees, "
                f"with {tool_result['description']}."
            )

        elif tool == "timer":
            answer = tool_result

        elif tool == "reminder":
            answer = tool_result

        elif tool == "application_launcher":
            answer = tool_result

        elif tool == "open_path":
            answer = tool_result

        elif tool == "search_files":
            answer = tool_result

        elif tool == "create_folder":
            answer = tool_result

        elif tool == "take_screenshot":
            answer = tool_result

        elif tool == "lock_computer":
            answer = tool_result

        elif tool == "website_launcher":
            answer = tool_result

        elif tool == "volume_up":
            answer = tool_result

        elif tool == "volume_down":
            answer = tool_result

        elif tool == "volume_mute":
            answer = tool_result

        elif tool == "volume_unmute":
            answer = tool_result

        elif tool == "volume_set":
            answer = tool_result

        else:
            answer = str(tool_result)

        add_message(
            "user",
            question
        )

        add_message(
            "assistant",
            answer
        )

        return answer

    # -------------------------
    # Determine question type
    # -------------------------

    route, rag_results = route_question(search_question)

    print("Question route:", route)

    # -------------------------
    # RAG Route
    # -------------------------

    if route == "rag":

        rag_results = filter_relevant_results(
            rag_results,
            threshold=0.5
        )

        print(
            "RAG results retrieved:",
            len(rag_results)
        )

        answer = generate_rag_answer(
            search_question,
            rag_results
        )

        if (
                "i don't have enough information" in answer.lower()
                or
                "not enough information" in answer.lower()
        ):

            print("RAG could not answer the question.")
            print("Falling back to General AI.")

            recent_conversation = get_recent_conversation(6)

            messages = [
                           {
                               "role": "system",
                               "content": SYSTEM_MESSAGE
                           }
                       ] + recent_conversation + [
                           {
                               "role": "user",
                               "content": f"""
            Answer this question as a voice assistant.

            Give ONLY the direct answer.
            Use 1–2 short sentences.
            Do not use headings.
            Do not use bullet points or numbered lists.
            Do not add extra explanation.

            Question:
            {search_question}
            """
                           }
                       ]

            response = ollama.chat(
                model="llama3.2:1b",
                messages=messages,
                options={
                    "num_predict": 240
                }
            )

            answer = response["message"]["content"].strip()


        else:

            print("RAG answered using the knowledge base.")

    # -------------------------
    # Uncertain Route
    # -------------------------

    elif route == "uncertain":

        print(

            "RAG relevance uncertain."

        )

        print(

            "Falling back to General AI."

        )

        recent_conversation = get_recent_conversation(6)

        messages = [
                       {
                           "role": "system",
                           "content": SYSTEM_MESSAGE
                       }
                   ] + recent_conversation + [
                       {
                           "role": "user",
                           "content": search_question
                       }
                   ]

        response = ollama.chat(

            model="llama3.2:1b",

            messages=messages,

            options={

                "num_predict": 240

            }

        )

        answer = response["message"]["content"].strip()

    # -------------------------
    # General AI Route
    # -------------------------

    else:

        print("RAG search skipped.")

        recent_conversation = get_recent_conversation(6)

        messages = [

                       {

                           "role": "system",

                           "content": SYSTEM_MESSAGE

                       }

                   ] + recent_conversation + [

                       {

                           "role": "user",

                           "content": f"""
        Answer this question as a voice assistant.

        Give ONLY the direct answer.
        Use 1–2 short sentences.
        Do not use headings.
        Do not use bullet points or numbered lists.
        Do not add extra explanation.

        Question:
        {search_question}
        """

                       }

                   ]

        response = ollama.chat(

            model="llama3.2:1b",

            messages=messages,

            options={

                "num_predict": 60,

                "temperature": 0.2

            }

        )

        answer = response["message"]["content"].strip()

    # -------------------------
    # Save Conversation
    # -------------------------

    add_message(
        "user",
        question
    )

    add_message(
        "assistant",
        answer
    )

    return answer


# -------------------------
# Warm Up AI Model
# -------------------------

def warm_up_model():
    print("Warming up AI model...")

    ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "user",
                "content": "Hello"
            }
        ],
        options={
            "num_predict": 1
        },
        keep_alive="10m"
    )

    print("AI model ready!")


# -------------------------
# Test AI
# -------------------------

if __name__ == "__main__":

    print("\nAI Test")
    print("Ask questions. Type 'exit' to stop.")

    while True:

        question = input("\n> ")

        if question.lower().strip() == "exit":
            break

        answer = ask_ai(question)

        print("\nAI Answer:")
        print(answer)

    print(
        "Calculator:",
        execute_tool("calculator", "25 * 48")
    )

    print(
        "Time:",
        execute_tool("time")
    )
