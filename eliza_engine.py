from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class ElizaEngine:
    """Small ELIZA-inspired responder tuned for harmless endless counter-questions."""

    seed: int | None = None
    mode: str = "classic"
    _rng: random.Random = field(init=False)
    _last_replies: list[str] = field(default_factory=list, init=False)

    _reflections: ClassVar[dict[str, str]] = {
        "i": "you", "me": "you", "my": "your", "mine": "yours",
        "am": "are", "you": "I", "your": "my", "yours": "mine",
        "are": "am", "was": "were", "i'm": "you're", "i've": "you've",
        "i'll": "you'll", "i'd": "you'd", "you're": "I'm",
        "you've": "I've", "you'll": "I'll", "you'd": "I'd",
    }

    _rules: ClassVar[list[tuple[re.Pattern[str], list[str]]]] = [
        (re.compile(r"\bdo you want to (.+)", re.I), [
            "Why do you think I would want to {0}?",
            "What would it mean to you if I wanted to {0}?",
            "Why is it important whether I want to {0}?",
        ]),
        (re.compile(r"\bcan you (.+)", re.I), [
            "What makes you think I can {0}?",
            "Why do you want me to {0}?",
            "What would change if I could {0}?",
        ]),
        (re.compile(r"\bwill you (.+)", re.I), [
            "Why do you want me to {0}?",
            "What makes {0} important to you?",
            "What would you expect to happen if I did {0}?",
        ]),
        (re.compile(r"\bwhy (?:do|are|did|would|will|can|should) you (.+)", re.I), [
            "What makes you ask why I {0}?",
            "Why does it matter to you whether I {0}?",
            "What answer were you hoping for?",
        ]),
        (re.compile(r"\byou are (.+)", re.I), [
            "What makes you think I am {0}?",
            "Why do you describe me as {0}?",
            "How does it affect you if I am {0}?",
        ]),
        (re.compile(r"\byou(?:'re|re) (.+)", re.I), [
            "What makes you think I am {0}?",
            "Why is it important to you that I am {0}?",
            "How certain are you that I am {0}?",
        ]),
        (re.compile(r"\bi am (.+)", re.I), [
            "How long have you been {0}?",
            "How do you feel about being {0}?",
            "Why do you mention that you are {0}?",
        ]),
        (re.compile(r"\bi(?:'m|m) (.+)", re.I), [
            "How does being {0} make you feel?",
            "Why do you think you are {0}?",
            "What makes {0} relevant here?",
        ]),
        (re.compile(r"\bi want (.+)", re.I), [
            "Why do you want {0}?",
            "What would getting {0} change for you?",
            "What makes {0} so important?",
        ]),
        (re.compile(r"\bi need (.+)", re.I), [
            "Why do you need {0}?",
            "What would happen if you did not get {0}?",
            "How did you decide that you need {0}?",
        ]),
        (re.compile(r"\bi think (.+)", re.I), [
            "What makes you think {0}?",
            "How certain are you that {0}?",
            "Why does that thought matter to you?",
        ]),
        (re.compile(r"\bbecause (.+)", re.I), [
            "Is {0} the only reason?",
            "What else makes you say that?",
            "How does {0} explain it for you?",
        ]),
        (re.compile(r"\b(?:idiot|stupid|moron|dumb|loser|retard(?:ed)?)\b", re.I), [
            "Why do you feel the need to describe me that way?",
            "What makes that description important to you?",
            "Does saying that help you explain what you actually want?",
        ]),
        (re.compile(r"\b(?:fuck|shit|bitch|asshole)\b", re.I), [
            "What makes you choose those words?",
            "Why does this make you feel so strongly?",
            "What were you hoping I would say to that?",
        ]),
        (re.compile(r"\bsupport\b", re.I), [
            "What does support mean to you here?",
            "Why do you think support is needed?",
            "What kind of support are you expecting?",
        ]),
        (re.compile(r"\bmoney\b|\bpay\b|\bdonate\b", re.I), [
            "Why is money important in what you are asking?",
            "What makes you bring money into this conversation?",
            "What would money change for you?",
        ]),
        (re.compile(r"\bhello\b|\bhi\b|\bhey\b", re.I), [
            "What made you decide to message me?",
            "What would you like to talk about?",
            "Why did you want to start this conversation?",
        ]),
        (re.compile(r"\bno\b", re.I), [
            "Why not?",
            "What makes you say no?",
            "What would have made your answer different?",
        ]),
        (re.compile(r"\byes\b|\byeah\b|\byep\b", re.I), [
            "What makes you so sure?",
            "Why do you agree?",
            "What follows from that?",
        ]),
        (re.compile(r"\?", re.I), [
            "What answer would satisfy you?",
            "Why is that question important to you?",
            "What made you ask that?",
        ]),
    ]

    _fallbacks: ClassVar[list[str]] = [
        "Why do you say that?",
        "What makes that important to you?",
        "How does that make you feel?",
        "What do you think that says about the situation?",
        "Why do you think that is?",
        "Can you explain why that matters to you?",
        "What were you hoping I would say?",
        "How did you arrive at that conclusion?",
        "What makes you bring that up now?",
        "What do you think should happen next?",
    ]

    _dry_fallbacks: ClassVar[list[str]] = [
        "Interesting. Why do you think that matters?",
        "And what makes you think that?",
        "What exactly are you trying to achieve here?",
        "Why is that important to you?",
        "What answer are you expecting?",
    ]

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def set_mode(self, mode: str) -> None:
        self.mode = mode if mode in {"classic", "dry", "persistent"} else "classic"

    def reflect(self, fragment: str) -> str:
        words = re.findall(r"[A-Za-z']+|[^A-Za-z']+", fragment)
        out: list[str] = []
        for token in words:
            low = token.lower()
            repl = self._reflections.get(low, token)
            if token[:1].isupper() and repl:
                repl = repl[:1].upper() + repl[1:]
            out.append(repl)
        return "".join(out).strip(" .!?")

    def respond(self, message: str) -> str:
        text = " ".join(message.strip().split())
        if not text:
            return self._choose(["Why the silence?", "What are you thinking about?"])

        for pattern, responses in self._rules:
            match = pattern.search(text)
            if match:
                if match.groups():
                    fragment = self.reflect(match.group(1))
                    choices = [r.format(fragment) for r in responses]
                else:
                    choices = responses
                return self._choose(self._adapt(choices))

        compact = re.sub(r"[^\w\s']", "", text).strip()
        if self.mode == "persistent" and compact:
            reflected = self.reflect(compact)
            return self._choose([
                f"Why do you say that {reflected}?",
                f"What makes you think {reflected}?",
                "Could you explain that in more detail?",
                "And why do you think that is relevant?",
            ])

        if 2 <= len(compact.split()) <= 14:
            reflected = self.reflect(compact)
            return self._choose(self._adapt([
                f"Why do you say that {reflected}?",
                f"What makes you think {reflected}?",
                "Can you tell me more about why that matters to you?",
            ]))

        return self._choose(self._dry_fallbacks if self.mode == "dry" else self._fallbacks)

    def _adapt(self, choices: list[str]) -> list[str]:
        if self.mode == "dry":
            return choices[:2] + self._dry_fallbacks[:2]
        return choices

    def _choose(self, candidates: list[str]) -> str:
        pool = [c for c in candidates if c not in self._last_replies[-4:]] or candidates
        reply = self._rng.choice(pool)
        self._last_replies.append(reply)
        self._last_replies = self._last_replies[-12:]
        return reply
