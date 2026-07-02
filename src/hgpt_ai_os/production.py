from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from hgpt_ai_os.content.generator import ContentGenerator
from hgpt_ai_os.content.export.docx_exporter import DocxExporter
from hgpt_ai_os.core.resource_path import resource_path
from hgpt_ai_os.intelligence import KnowledgeSearch, TopicAnalyzer
from hgpt_ai_os.knowledge.bundle import KnowledgeBundle
from hgpt_ai_os.version import APP_VERSION


OUTPUT_ROOT = (
    Path.home()
    / "Documents"
    / "LUCID"
    / "outputs"
    / "marketing"
)


def build_outputs(day: int, topic: str, open_output_folder: bool = True) -> Path:
    start = time.time()

    print("=" * 60)
    print(f"LUCID AUTO {APP_VERSION}")
    print("HGPT STEEL PRODUCTION CLI")
    print("=" * 60)
    print(f"Day   : {day:03d}")
    print(f"Topic : {topic}")
    print("-" * 60)

    print("[01/08] Analyze Topic                    PASS")
    analysis = TopicAnalyzer().analyze(topic)
    print(f"Analysis  : {analysis.category} | {analysis.process}")
    print(f"Operation : {analysis.operation or 'Unknown'}")
    print(f"Risk      : {analysis.risk or 'None'}")
    print(
        "Standards : "
        + (", ".join(analysis.standards) if analysis.standards else "None")
    )

    knowledge_root = resource_path("knowledge") if getattr(sys, "frozen", False) else "knowledge"
    print("[02/08] Search Knowledge                 PASS")
    items = KnowledgeSearch(knowledge_root).search(analysis, top_k=5)
    if not items:
        print("Knowledge Search : 0 item(s), continuing normally")

    print("[03/08] Build Knowledge Context          PASS")
    bundle = KnowledgeBundle(query=topic, items=items)
    context = bundle.context()

    print("[04/08] Initialize Generator             PASS")
    generator = ContentGenerator()

    print("[05/08] Generate Content                 PASS")
    files = {
        "facebook.docx": generator.generate_facebook(topic, context),
        "tiktok.docx": generator.generate_tiktok(topic, context),
        "image_prompt.docx": generator.generate_image_prompt(topic, context),
        "video_prompt.docx": generator.generate_video_prompt(topic, context),
        "seo.docx": generator.generate_seo(topic, context),
        "hashtags.docx": generator.generate_hashtags(),
        "approval_checklist.docx": generator.generate_checklist(),
    }

    print("[06/08] Prepare Output Folder            PASS")
    output_dir = OUTPUT_ROOT / f"Day{day:03d}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[07/08] Export DOCX                      PASS")
    exporter = DocxExporter()
    for filename, content in files.items():
        exporter.save(output_dir / filename, topic, content)

    print("[08/08] Production Completed             PASS")
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
