"""Provider initialization, health monitoring, retry, and availability."""

from __future__ import annotations

from hgpt_ai_os.contracts.diagnostics_contract import ContractError, PlatformErrorCode
from hgpt_ai_os.contracts.provider_contract import Provider, ProviderError, ProviderRequest
from hgpt_ai_os.providers.base_provider import ProviderAdapterUnavailable
from hgpt_ai_os.providers.provider_factory import ProviderFactory
from hgpt_ai_os.providers.provider_health import ProviderHealthSnapshot, ProviderHealthStatus
from hgpt_ai_os.providers.provider_registry import ProviderRegistry
from hgpt_ai_os.providers.provider_result import ProviderExecutionResult
from hgpt_ai_os.providers.provider_selector import ProviderSelector


class ProviderManager:
    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        factory: ProviderFactory | None = None,
    ) -> None:
        self.registry = registry or ProviderRegistry()
        self.factory = factory or ProviderFactory()
        self.selector = ProviderSelector(self.registry)

    def initialize_providers(self, provider_ids: tuple[str, ...] | None = None) -> None:
        ids = provider_ids or self.factory.available_provider_ids()
        for provider_id in ids:
            if not self.registry.contains(provider_id):
                self.registry.register(self.factory.create(provider_id))

    def health(self, provider_id: str) -> ProviderHealthSnapshot:
        provider = self.registry.get(provider_id)
        health = provider.health()
        return ProviderHealthSnapshot(
            provider_id=provider_id,
            status=ProviderHealthStatus(health.report.status),
            metadata=health.report.metadata,
        )

    def health_report(self) -> tuple[ProviderHealthSnapshot, ...]:
        return tuple(self.health(provider_id) for provider_id in self.registry.provider_ids())

    def available_provider_ids(self) -> tuple[str, ...]:
        return tuple(snapshot.provider_id for snapshot in self.health_report() if snapshot.available)

    def is_available(self, provider_id: str) -> bool:
        return self.health(provider_id).available

    def execute(
        self,
        provider_id: str,
        request: ProviderRequest,
        *,
        retries: int = 0,
    ) -> ProviderExecutionResult:
        provider = self.registry.get(provider_id)
        attempts = 0
        last_error: ProviderError | None = None
        for attempts in range(1, max(0, retries) + 2):
            result = self._try_generate(provider, request, attempts)
            if result.ok:
                return result
            last_error = result.error
            if last_error is None or not last_error.retryable:
                return result
        return ProviderExecutionResult(
            provider_id=provider_id,
            error=last_error,
            attempts=attempts,
        )

    def _try_generate(
        self,
        provider: Provider,
        request: ProviderRequest,
        attempts: int,
    ) -> ProviderExecutionResult:
        provider_id = provider.metadata.provider_id
        try:
            response = provider.generate(request)
        except ProviderAdapterUnavailable as exc:
            return ProviderExecutionResult(
                provider_id=provider_id,
                error=self._provider_error(provider_id, request.request_id, str(exc), retryable=False),
                attempts=attempts,
            )
        except Exception as exc:
            return ProviderExecutionResult(
                provider_id=provider_id,
                error=self._provider_error(provider_id, request.request_id, str(exc), retryable=True),
                attempts=attempts,
            )
        return ProviderExecutionResult(provider_id=provider_id, response=response, attempts=attempts)

    def _provider_error(
        self,
        provider_id: str,
        request_id: str,
        message: str,
        *,
        retryable: bool,
    ) -> ProviderError:
        return ProviderError(
            error=ContractError(
                code=PlatformErrorCode.PROVIDER_UNAVAILABLE,
                message=message,
                source="provider_manager",
            ),
            provider_id=provider_id,
            request_id=request_id,
            retryable=retryable,
        )
