from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional


@dataclass
class KnowledgeMetadata:
    id: str
    title: str
    category: str
    tags: List[str] = field(default_factory=list)
    author: str = "MaithuyELEC"
    version: str = "1.0"
    status: str = "draft"
    source_path: Optional[str] = None
    related: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgePackage:
    metadata: KnowledgeMetadata
    content: str

    @property
    def id(self):
        return self.metadata.id

    @property
    def title(self):
        return self.metadata.title

    @property
    def category(self):
        return self.metadata.category

    @property
    def tags(self):
        return self.metadata.tags


@dataclass
class KnowledgeResult:
    item: KnowledgePackage
    score: float
    matched_keywords: List[str] = field(default_factory=list)
    matched_rules: List[str] = field(default_factory=list)
