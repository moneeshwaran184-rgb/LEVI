"""Text preparation shared by streaming and ordinary speech."""
import re


def clean_speech(text):
    text = re.sub(r"```[\s\S]*?```", "Code omitted.", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[0-9#*]\ufe0f?\u20e3", "", text)
    text = re.sub("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2300-\u23FF\uFE0E\uFE0F\u200D\u20E3]", "", text)
    text = re.sub(r"[`*_#]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def asks_question(text):
    text = clean_speech(text).rstrip(' \"\u201d\u2019\')]}' )
    # Only a final direct question opens the microphone, not a quoted question
    # or generic phrases such as "let me know" in an ordinary answer.
    return text.endswith("?")
