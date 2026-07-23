from .context_builder import PromptContext, build_context
from .knowledge_expander import expand
from .response_contract import RESPONSE_CONTRACT

def build_user_prompt(topic: str) -> str:
    ctx = PromptContext(topic=topic)

    knowledge = expand(topic)

    sections = "\n".join(f"- {item}" for item in knowledge)

    outputs = "\n".join(f"- {item}" for item in RESPONSE_CONTRACT)

    return f"""
# CONTEXT

{build_context(ctx)}

# KNOWLEDGE

{sections}

# OUTPUT REQUIREMENTS

Hãy tạo đầy đủ các phần sau:

{outputs}

# TOPIC

{topic}
"""
