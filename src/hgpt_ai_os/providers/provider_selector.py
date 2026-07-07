"""Automatic provider and model selection."""

from __future__ import annotations

from hgpt_ai_os.contracts.provider_contract import ProviderMetadata
from hgpt_ai_os.providers.provider_policy import ProviderPolicyMode, ProviderSelectionPolicy
from hgpt_ai_os.providers.provider_registry import ProviderRegistry
from hgpt_ai_os.providers.provider_result import ProviderSelectionResult


class ProviderSelector:
    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def select(self, policy: ProviderSelectionPolicy | None = None) -> ProviderSelectionResult:
        active_policy = policy or ProviderSelectionPolicy()
        candidates = [
            metadata
            for metadata in self.registry.discover(active_policy.required_capability)
            if active_policy.allows_provider(metadata.provider_id)
        ]
        candidates = [metadata for metadata in candidates if self._matches_mode(metadata, active_policy)]
        if not candidates:
            raise LookupError("no provider satisfies the selection policy")

        ordered = tuple(sorted(candidates, key=lambda metadata: self._score(metadata, active_policy)))
        selected = ordered[0]
        model = self._select_model(selected, active_policy.preferred_model)
        return ProviderSelectionResult(
            provider_id=selected.provider_id,
            model=model,
            metadata=selected,
            fallback_chain=tuple(metadata.provider_id for metadata in ordered[1:]),
            policy_metadata={"mode": active_policy.mode.value},
        )

    def fallback_chain(self, policy: ProviderSelectionPolicy | None = None) -> tuple[str, ...]:
        result = self.select(policy)
        return (result.provider_id, *result.fallback_chain)

    def _matches_mode(self, metadata: ProviderMetadata, policy: ProviderSelectionPolicy) -> bool:
        if policy.mode is ProviderPolicyMode.OFFLINE:
            return bool(metadata.metadata.get("offline", False))
        if policy.mode is ProviderPolicyMode.PRIVACY:
            return bool(metadata.metadata.get("privacy_preserving", False))
        if policy.mode is ProviderPolicyMode.ENTERPRISE and policy.enterprise_providers:
            return metadata.provider_id in policy.enterprise_providers
        return True

    def _score(self, metadata: ProviderMetadata, policy: ProviderSelectionPolicy) -> tuple[int, int, int, str]:
        free_penalty = 0 if metadata.metadata.get("free", False) else 1
        offline_penalty = 0 if metadata.metadata.get("offline", False) else 1
        cost_rank = int(metadata.metadata.get("cost_rank", 100))
        latency_rank = int(metadata.metadata.get("latency_rank", 100))

        primary = free_penalty if policy.free_first else 0
        if policy.offline_preference:
            primary = offline_penalty
        if policy.cost_preference:
            return (primary, cost_rank, latency_rank, metadata.provider_id)
        if policy.latency_preference:
            return (primary, latency_rank, cost_rank, metadata.provider_id)
        return (primary, cost_rank, latency_rank, metadata.provider_id)

    def _select_model(self, metadata: ProviderMetadata, preferred_model: str | None) -> str | None:
        models = tuple(metadata.metadata.get("models", ()))
        if preferred_model and preferred_model in models:
            return preferred_model
        default_model = metadata.metadata.get("default_model")
        if isinstance(default_model, str) and default_model:
            return default_model
        if models:
            return models[0]
        return None
