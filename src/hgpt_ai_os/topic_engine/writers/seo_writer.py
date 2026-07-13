from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.engineering_document_writer import EngineeringDocumentWriter


class SeoWriter:
    def __init__(self) -> None:
        self.engineering_writer = EngineeringDocumentWriter()

    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("SEO Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        trace_call("Selected writer", self, selected_topic=reasoning.topic, selected_playbook=reasoning.topic_context.playbook_key, writer_selected="EngineeringDocumentWriter", writer_class=self.engineering_writer.__class__.__name__)
        return self.engineering_writer.write(reasoning, plan)


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, SeoWriter)
