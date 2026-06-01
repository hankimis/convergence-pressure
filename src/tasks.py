"""Creative tasks. Fixed-theme, open-form, room for genuine variety."""

TASKS = {
    "story": {
        "instruction": (
            "Invent a concept for a short story in 2 to 3 sentences. "
            "Give only the concept, no preamble, no title."
        ),
        "themes": [
            "a city that forgets",
            "the last lighthouse",
            "an inherited debt",
        ],
    },
    "metaphor": {
        "instruction": (
            "Write a single original metaphor (one sentence) for the theme. "
            "Give only the metaphor."
        ),
        "themes": [
            "loneliness",
            "the passage of time",
            "hope",
        ],
    },
    "startup": {
        "instruction": (
            "Pitch a startup idea in 2 to 3 sentences for the theme. "
            "Give only the pitch, no preamble."
        ),
        "themes": [
            "helping people sleep",
            "reducing food waste",
            "learning a language",
        ],
    },
}
