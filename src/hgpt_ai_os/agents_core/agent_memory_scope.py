"""Universal agent memory scope model."""

from __future__ import annotations

from enum import Enum


class AgentMemoryScope(str, Enum):
    CONVERSATION = "conversation"
    SESSION = "session"
    PROJECT = "project"
    TEMPORARY = "temporary"
    READ_ONLY = "read_only"
