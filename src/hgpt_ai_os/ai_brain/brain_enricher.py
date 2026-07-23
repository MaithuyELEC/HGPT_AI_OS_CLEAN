from dataclasses import replace

from hgpt_ai_os.engineering_pipeline.prompt_composer import ComposedPrompt

from .knowledge_expander import expand
from .response_contract import RESPONSE_CONTRACT
from .prompt_version import PROMPT_VERSION


class BrainEnricher:
    """
    Enrich PromptComposer output without changing PromptComposer itself.
    """

    @staticmethod
    def enrich(prompt: ComposedPrompt, topic: str) -> ComposedPrompt:

        knowledge = "\n".join(
            f"- {item}" for item in expand(topic)
        )

        outputs = "\n".join(
            f"- {item}" for item in RESPONSE_CONTRACT
        )

        extra = f"""

=========================
Lucid GPT Brain {PROMPT_VERSION}
=========================

## Expanded Knowledge

{knowledge}

## Required Outputs

{outputs}

"""

        return replace(
            prompt,
            user_prompt=prompt.user_prompt + "\n\n" + extra,
        )
