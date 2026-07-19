from dataclasses import dataclass

@dataclass
class PromptContext:
    topic: str
    domain: str = "Industrial / Business / General"
    audience: str = "Professional"
    language: str = "Vietnamese"
    output: str = "7 DOCX"

def build_context(ctx: PromptContext) -> str:
    return f"""
Topic:
{ctx.topic}

Domain:
{ctx.domain}

Audience:
{ctx.audience}

Language:
{ctx.language}

Expected Output:
{ctx.output}
"""
