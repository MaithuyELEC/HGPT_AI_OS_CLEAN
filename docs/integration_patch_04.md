# Integration Patch 04

## Goal

Lock the desktop production path so free users can generate DOCX outputs
without OpenAI, Gemini, Anthropic, Ollama, or provider configuration.

## Result

The desktop path remains:

Desktop
-> ProductionWorker
-> ProductionService
-> PlatformRuntime.execute()
-> platform legacy adapter
-> legacy production builder

`ProductionService().run(topic)` completes through the runtime-routed legacy
adapter even when AI provider settings and API tokens are empty. The AI layer
remains optional; missing providers are converted into generated fallback
content and DOCX export still completes.

## Boundary

No GUI layout, DOCX format, generated output structure, AI prompts, provider
architecture, runtime contracts, agents, knowledge, plugins, marketplace, or
packaging code changed.
