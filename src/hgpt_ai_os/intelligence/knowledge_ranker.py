from __future__ import annotations

import re

from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis
from hgpt_ai_os.knowledge.models import KnowledgePackage, KnowledgeResult


class KnowledgeRanker:
    def rank(
        self,
        analysis: TopicAnalysis,
        items: list[KnowledgePackage],
    ) -> list[KnowledgeResult]:
        results = [
            self._rank_item(analysis, item)
            for item in items
        ]

        results.sort(key=lambda result: result.score, reverse=True)
        return results

    def _rank_item(
        self,
        analysis: TopicAnalysis,
        item: KnowledgePackage,
    ) -> KnowledgeResult:
        text = self._item_text(item)
        matched_keywords = [
            keyword
            for keyword in analysis.keywords
            if self._normalize(keyword) in text
        ]
        matched_rules: list[str] = []
        score = 0.0

        if analysis.keywords:
            score += 0.35 * (len(matched_keywords) / len(analysis.keywords))

        if self._matches(analysis.category, text):
            score += 0.20
            matched_rules.append(f"category:{analysis.category}")

        if self._matches(analysis.process, text, ignored={"unknown"}):
            score += 0.15
            matched_rules.append(f"process:{analysis.process}")

        matched_standards = [
            standard
            for standard in analysis.standards
            if self._matches(standard, text)
        ]
        if analysis.standards:
            score += 0.20 * (len(matched_standards) / len(analysis.standards))
            matched_rules.extend(f"standard:{standard}" for standard in matched_standards)

        if self._matches(analysis.risk, text):
            score += 0.10
            matched_rules.append(f"risk:{analysis.risk}")

        return KnowledgeResult(
            item=item,
            score=round(min(score, 1.0), 2),
            matched_keywords=matched_keywords,
            matched_rules=matched_rules,
        )

    def _item_text(self, item: KnowledgePackage) -> str:
        return self._normalize(
            " ".join([
                item.id,
                item.title,
                item.category,
                " ".join(item.tags),
                item.content,
            ])
        )

    def _matches(
        self,
        value: str,
        text: str,
        ignored: set[str] | None = None,
    ) -> bool:
        normalized = self._normalize(value)
        if not normalized:
            return False
        if ignored and normalized in ignored:
            return False
        return normalized in text

    def _normalize(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.lower().replace("-", " ")).strip()
