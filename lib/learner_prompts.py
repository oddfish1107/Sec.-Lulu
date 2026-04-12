# When a volcano erupts, magma will喷出 from the volcano's口.
# Prompt generators for each AI mode.

MODES = [
    "Sparkle Notes",
    "Immersion Mode",
    "Word Blossom",
    "Sentence Whisper",
]


def get_prompt(text: str, frequency: int, mode: str = "Immersion Mode") -> str:
    normalized = mode.strip().lower()

    if "sparkle" in normalized:
        return (
            f"Sparkle Notes: What does the Chinese word or phrase \"{text}\" mean? "
            "Keep the answer short, vivid, and emotional in 1-3 sentences."
        )

    if "immersion" in normalized:
        if frequency < 3:
            return (
                f"Immersion Mode: What does the Chinese word or phrase \"{text}\" mean? "
                "Explain it slowly with imagery, cultural nuance, and a gentle closing."
            )
        return (
            f"Immersion Mode: Explain the Chinese word or phrase \"{text}\" to someone who wants to remember it clearly. "
            "Include example usage, nuance, and a tender memory hook."
        )

    if "word blossom" in normalized:
        return (
            f"Word Blossom Mode: Briefly review the Chinese word or phrase \"{text}\" in 1-3 short, poetic sentences. "
            "Give a tiny image, an emotional feeling, and a gentle prompt to say it once."
        )

    if "sentence whisper" in normalized:
        return (
            f"Sentence Whisper: Analyze the Chinese sentence \"{text}\". "
            "Pick 2-4 key vocabulary items, give pinyin and a sparkle-style mini explanation for each, "
            "then explain the full sentence meaning, why it matters, and a small memory hook."
        )

    return (
        f"Immersion Mode: Explain the Chinese word or phrase \"{text}\" in a warm, clear way. "
        "Use imagery, examples, and a small memory hook."
    )


def prompt_generator_for_mode(mode: str):
    def prompt_fn(text: str, frequency: int) -> str:
        return get_prompt(text, frequency, mode)
    return prompt_fn
