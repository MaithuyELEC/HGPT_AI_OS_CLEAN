# Universal Marketplace Foundation

Sprint 08 introduces the metadata-only marketplace foundation. It creates an
isolated `hgpt_ai_os.marketplace` package for package registration, cataloging,
repository metadata, installer planning, validation, security review, signing
metadata, review lifecycle, release channels, update state, publisher profiles,
dependency metadata, compatibility metadata, and marketplace metrics.

The foundation does not download packages, call remote services, execute
marketplace code, modify the Plugin SDK, or connect to GUI, provider, runtime,
agent, knowledge, production, or AI generation workflows.

## Marketplace Architecture

The marketplace layer is split into small metadata services:

- `MarketplaceManifest` describes a package.
- `MarketplaceRegistry` registers, removes, and discovers package metadata.
- `MarketplaceCatalog` indexes packages by type and capability.
- `RepositoryRegistry` stores repository metadata.
- `MarketplaceInstaller` records install lifecycle plans and validates metadata.
- `MarketplaceValidator` checks manifests, compatibility, dependencies, and integrity metadata.
- `MarketplaceSecurity` reviews publisher trust, package trust, permissions, sandbox needs, and audit metadata.
- `MarketplaceSigning` stores certificate and signature metadata for future PKI integration.
- `ReviewRecord` controls the package review lifecycle.
- `MarketplaceUpdates` represents installed, available, ignored, pinned, and rollback update states.
- `MarketplaceMetrics` records local marketplace counters.

## Repository Model

The repository model is architecture-only. Repository records include an ID,
name, type, enabled flag, and priority. Supported repository types are:

- Official
- Community
- Enterprise
- Private
- Local
- Offline

The model intentionally has no HTTP client, cloud client, download command,
upload command, credential store, or package transport implementation.

## Package Lifecycle

Marketplace review lifecycle states are:

- Draft
- Submitted
- Verified
- Approved
- Rejected
- Deprecated
- Archived

Install lifecycle planning supports install, uninstall, upgrade, downgrade, and
rollback. Each action validates dependency metadata and compatibility metadata
before changing the local in-memory registry state.

## Publisher Trust Model

Publisher profiles include:

- Publisher ID
- Organization
- Trust level
- Verification status
- Signing status

Trust levels include unknown, community, verified, official, and enterprise.
Security review combines publisher verification, signing metadata, checksum
presence, declared permissions, sandbox requirement, and audit metadata into a
metadata-only trust decision.

## Package Compatibility

Package compatibility metadata includes:

- Platform version
- Contract version
- Provider version
- Plugin SDK version
- Supported platforms

The compatibility evaluator compares package minimum versions with the current
platform metadata and returns compatible, upgrade required, or incompatible.
This preserves backward compatibility because no existing runtime contract is
changed or imported by the marketplace package.

## Dependency Resolution

Dependency metadata supports:

- Required dependencies
- Optional dependencies
- Conflicts
- Replaces

The validator reports missing required packages and installed conflicts. It does
not install dependencies, resolve remote packages, or alter any package outside
the local marketplace registry.

## Security Architecture

Security is metadata-only in Sprint 08. The security module records publisher
trust, package trust, permission review, sandbox requirement, and audit metadata.
Signing stores certificate metadata, signature metadata, a verification model,
and signature status. The verification model is future-PKI-ready without
performing certificate-chain validation or remote revocation checks.

## Future Cloud Integration

Future cloud marketplace integration can attach transport, authentication,
package download, telemetry, payment, and enterprise policy services around the
metadata foundation. Those integrations are deliberately outside this sprint, so
the local platform remains functional without cloud connectivity or marketplace
availability.
