from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from hgpt_ai_os.content.export.docx_exporter import DocxExporter
from hgpt_ai_os.core.resource_path import resource_path
from hgpt_ai_os.diagnostics import engine_loaded, instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.engineering_pipeline import EngineeringGenerationPipeline
from hgpt_ai_os.intelligence import KnowledgeSearch, TopicAnalyzer
from hgpt_ai_os.knowledge.bundle import KnowledgeBundle
from hgpt_ai_os.knowledge.models import KnowledgeMetadata, KnowledgePackage, KnowledgeResult
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine, compact_topic_context
from hgpt_ai_os.topic_engine.engineering_knowledge_library import (
    EngineeringKnowledgeLibrary,
    EngineeringPlaybook,
    EngineeringRootCause,
)
from hgpt_ai_os.version import APP_VERSION


OUTPUT_ROOT = (
    Path.home()
    / "Documents"
    / "LUCID"
    / "outputs"
    / "marketing"
)


def build_outputs(day: int, topic: str, open_output_folder: bool = True) -> Path:
    trace_call("Production.build_outputs", None, selected_topic=topic)
    start = time.time()

    print("=" * 60)
    print(f"Lucid AI Studio {APP_VERSION}")
    print("HGPT STEEL PRODUCTION CLI")
    print("=" * 60)
    print(f"Day   : {day:03d}")
    print(f"Topic : {topic}")
    print("-" * 60)

    print("[01/08] Analyze Topic                    PASS")
    topic_engine = TopicIntelligenceEngine()
    topic_context = topic_engine.analyze(topic)
    analysis = topic_context.to_topic_analysis()
    trace_call(
        "Topic Engine.analyze",
        topic_engine,
        selected_topic=topic,
        selected_domain=topic_context.domain,
        selected_playbook=topic_context.playbook_key,
        writer_selected="pending",
        writer_class="pending",
        knowledge_count="pending",
        output_file="pending",
    )
    print(f"Analysis  : {analysis.category} | {analysis.process}")
    print(f"Operation : {analysis.operation or 'Unknown'}")
    print(f"Risk      : {analysis.risk or 'None'}")
    print("Topic Context:")
    print(compact_topic_context(topic_context))
    print(
        "Standards : "
        + (", ".join(analysis.standards) if analysis.standards else "None")
    )

    knowledge_root = resource_path("knowledge") if getattr(sys, "frozen", False) else "knowledge"
    print("[02/08] Search Knowledge                 PASS")
    items = KnowledgeSearch(knowledge_root).search(analysis, top_k=5)
    items = _with_engineering_playbook(items, topic_context)
    if not items:
        print("Knowledge Search : 0 item(s), continuing normally")

    print("[03/08] Build Knowledge Context          PASS")
    bundle = KnowledgeBundle(query=topic, items=items)
    context = bundle.context()

    print("[04/08] Initialize AI Engineering Pipeline PASS")
    pipeline = EngineeringGenerationPipeline()
    trace_call(
        "AI Engineering Pipeline initialized",
        pipeline,
        selected_topic=topic,
        selected_domain=topic_context.domain,
        selected_playbook=topic_context.playbook_key,
        writer_selected="EngineeringGenerationPipeline",
        writer_class=pipeline.__class__.__name__,
        knowledge_count=len(items),
        output_file="pending",
    )
    if pipeline.free_desktop_mode:
        print("Mode : Offline Mode")
        print("⚠ Offline Mode")
        print("You are using the Local Engine.")
        print("AI-quality generation is unavailable.")
        print("Generated content quality will be lower.")
    else:
        print(f"Mode : AI Mode ({pipeline.validation.config.provider.title()})")
        print(f"Active Provider : {pipeline.validation.config.provider.title()}")

    output_dir = OUTPUT_ROOT / f"Day{day:03d}"
    engine_loaded(
        pipeline,
        selected_topic=topic,
        selected_playbook=topic_context.playbook_key,
        knowledge_count=len(items),
        selected_writer="EngineeringGenerationPipeline",
        output_folder=output_dir,
    )

    try:
        print("[05/08] Generate Engineering Record      PASS")
        engineering_record, files = pipeline.generate_documents(
            topic=topic,
            context=context,
            knowledge_items=items,
            topic_context=topic_context,
        )
        print(f"Request ID : {pipeline.request_id}")
        print(f"Fingerprint: {pipeline.topic_fingerprint}")
        print(f"Intent     : {engineering_record.primary_domain} | {engineering_record.topic_type}")
        print(f"Entity     : {engineering_record.main_entity}")
        trace_call(
            "Engineering Record generated",
            pipeline,
            selected_topic=topic,
            selected_domain=engineering_record.domain,
            selected_playbook=topic_context.playbook_key,
            writer_selected="EngineeringRecord",
            writer_class=engineering_record.__class__.__name__,
            knowledge_count=len(items),
            output_file="pending",
        )

        print("[06/08] Prepare Output Folder            PASS")
        output_dir.mkdir(parents=True, exist_ok=True)
        trace_call(
            "Output folder selected",
            None,
            selected_topic=topic,
            selected_domain=topic_context.domain,
            selected_playbook=topic_context.playbook_key,
            knowledge_count=len(items),
            output_file=output_dir,
        )

        print("[07/08] Export DOCX                      PASS")
        exporter = DocxExporter()
        for filename, content in files.items():
            trace_call(
                "DOCX Writer",
                exporter,
                selected_topic=topic,
                output_file=output_dir / filename,
                final_docx_writer=exporter.__class__.__name__,
            )
            exporter.save(output_dir / filename, topic, content)
        pipeline.docx_created = True
    except Exception:
        _print_v21_log(pipeline)
        raise

    print("[08/08] Production Completed             PASS")
    _print_v21_log(pipeline)
    print("-" * 60)
    print("STATUS    : PRODUCTION SUCCESS")
    print(f"Knowledge : {len(items)} item(s)")
    print(f"Output    : {output_dir}")

    if open_output_folder and sys.platform == "darwin":
        import subprocess

        subprocess.run(["open", str(output_dir)])

    print(f"Elapsed   : {time.time() - start:.2f} seconds")
    print("=" * 60)

    return output_dir


def _print_v21_log(pipeline: EngineeringGenerationPipeline) -> None:
    print(f"Provider : {pipeline.provider}")
    print(f"Model : {pipeline.model}")
    print(f"HTTP Status : {pipeline.http_status}")
    print(f"Error : {pipeline.error}")
    print(
        "EngineeringRecord Created = "
        + ("YES" if pipeline.engineering_record_created else "NO")
    )
    print("DOCX Created = " + ("YES" if pipeline.docx_created else "NO"))


def _with_engineering_playbook(items: list[KnowledgeResult], topic_context) -> list[KnowledgeResult]:
    playbook_key = getattr(topic_context, "playbook_key", "")
    if not playbook_key:
        return items

    playbook = EngineeringKnowledgeLibrary().get(playbook_key)
    if playbook is None:
        return items

    if any(result.item.id == playbook.key for result in items):
        return items

    return [
        *items,
        KnowledgeResult(
            item=KnowledgePackage(
                metadata=KnowledgeMetadata(
                    id=playbook.key,
                    title=playbook.process,
                    category=playbook.domain,
                    tags=[*playbook.equipment[:5], *playbook.failure_modes[:3]],
                    source_path="hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json",
                ),
                content=_engineering_playbook_content(playbook),
            ),
            score=1.0,
            matched_keywords=list(topic_context.signals),
            matched_rules=[f"playbook:{playbook.key}"],
        ),
    ]


def _engineering_playbook_content(playbook: EngineeringPlaybook) -> str:
    sections = [
        ("Equipment", playbook.equipment),
        ("Failure mechanism", playbook.failure_mechanism),
        ("Failure modes", playbook.failure_modes),
        ("Symptoms", playbook.symptoms),
        ("Root cause tree", playbook.root_cause_tree),
        ("Inspection procedure", playbook.inspection_procedure),
        ("Measuring instruments", playbook.measuring_instruments),
        ("Measurements", playbook.measurements),
        ("Acceptance criteria", playbook.acceptance_criteria),
        ("Related standards", playbook.related_standards),
        ("Repair procedure", playbook.repair_procedure_sop),
        ("Verification after repair", playbook.verification_after_repair),
        ("Preventive maintenance", playbook.preventive_maintenance),
        ("Common mistakes", playbook.common_mistakes),
        ("Lessons learned", playbook.lessons_learned),
        ("Digital factory recommendations", playbook.digital_factory_recommendations),
        ("Safety risks", playbook.safety_risks),
        ("Quality risks", playbook.quality_risks),
    ]
    lines = [f"Process: {playbook.process}", f"Production impact: {playbook.production_impact}"]
    for label, values in sections:
        lines.append(label + ":")
        lines.extend(f"- {value}" for value in values)
    lines.append("Root causes:")
    for root_cause in playbook.root_causes:
        lines.extend(_root_cause_lines(root_cause))
    return "\n".join(line for line in lines if line)


def _root_cause_lines(root_cause: EngineeringRootCause) -> list[str]:
    return [
        f"- Cause: {root_cause.cause}",
        f"  Category: {root_cause.category}",
        f"  Symptoms: {'; '.join(root_cause.symptoms)}",
        f"  Inspection: {'; '.join(root_cause.inspection)}",
        f"  Instruments: {'; '.join(root_cause.instruments)}",
        f"  Measurements: {'; '.join(root_cause.measurements)}",
        f"  Acceptance: {'; '.join(root_cause.acceptance)}",
        f"  Repair: {'; '.join(root_cause.repair)}",
        f"  Verification: {'; '.join(root_cause.verification)}",
        f"  Prevention: {'; '.join(root_cause.prevention)}",
    ]



def next_day() -> int:
    root = OUTPUT_ROOT

    if not root.exists():
        return 1

    days = []

    for d in root.iterdir():
        if d.is_dir() and d.name.startswith("Day"):
            try:
                days.append(int(d.name[3:]))
            except ValueError:
                pass

    return max(days, default=0) + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str)
    args = parser.parse_args()

    topic = args.topic

    if not topic:
        topic = input("Topic: ").strip()

    if not topic:
        print("ERROR : Topic is required.", file=sys.stderr)
        return 1

    day = next_day()

    try:
        build_outputs(day, topic)
    except Exception as exc:
        print("STATUS : PRODUCTION FAILED", file=sys.stderr)
        print(f"ERROR  : {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, None)
