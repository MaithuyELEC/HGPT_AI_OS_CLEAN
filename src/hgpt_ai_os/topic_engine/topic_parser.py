from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "và",
    "của",
    "cho",
    "khi",
    "tại",
    "trong",
    "ngoài",
    "với",
    "về",
    "là",
    "các",
    "một",
    "những",
    "này",
    "để",
    "do",
    "bị",
    "cần",
}


@dataclass(frozen=True)
class ParsedTopic:
    original: str
    normalized: str
    tokens: tuple[str, ...]
    keywords: tuple[str, ...]
    phrases: tuple[str, ...]


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFC", (text or "").strip().lower())
    value = re.sub(r"[^\wÀ-ỹ\s/+.-]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[\wÀ-ỹ/+.-]+", normalize(text)))


def remove_stop_words(tokens: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(token for token in tokens if len(token) > 1 and token not in STOP_WORDS)


def extract_phrases(tokens: tuple[str, ...]) -> tuple[str, ...]:
    phrases: list[str] = []
    for size in (3, 2):
        for index in range(max(len(tokens) - size + 1, 0)):
            phrase = " ".join(tokens[index : index + size])
            if any(word not in STOP_WORDS for word in phrase.split()):
                phrases.append(phrase)
    return tuple(dict.fromkeys(phrases))


def build_keywords(text: str) -> tuple[str, ...]:
    tokens = remove_stop_words(tokenize(text))
    phrases = extract_phrases(tokens)
    return tuple(dict.fromkeys((*phrases, *tokens)))


class TopicParser:
    def parse(self, topic: str) -> ParsedTopic:
        tokens = tokenize(topic)
        useful_tokens = remove_stop_words(tokens)
        phrases = extract_phrases(useful_tokens)
        return ParsedTopic(
            original=(topic or "").strip(),
            normalized=normalize(topic),
            tokens=tokens,
            keywords=tuple(dict.fromkeys((*phrases, *useful_tokens))),
            phrases=phrases,
        )
