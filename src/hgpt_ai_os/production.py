from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from hgpt_ai_os.content.generator import ContentGenerator
from hgpt_ai_os.content.export.docx_exporter import DocxExporter
from hgpt_ai_os.core.resource_path import resource_path
from hgpt_ai_os.knowledge.bundle import KnowledgeBundle
from hgpt_ai_os.knowledge.retriever import KnowledgeRetriever


OUTPUT_ROOT = (
    Path.home()
    / "Documents"
    / "LUCID"
    / "outputs"
    / "marketing"
)


def build_outputs(day: int, topic: str) -> Path:
    start = time.time()

    print("=" * 60)
    print("LUCID AUTO v1.0.1")
    print("HGPT STEEL PRODUCTION CLI")
    print("=" * 60)
    print(f"Day   : {day:03d}")
    print(f"Topic : {topic}")
    print("-" * 60)

    print("[01/07] Load Knowledge                   PASS")
    knowledge_root = resource_path("knowledge") if getattr(sys, "frozen", False) else "knowledge"
    retriever = KnowledgeRetriever(knowledge_root)
    items = retriever.retrieve(topic, top_k=5)

    print("[02/07] Build Knowledge Context          PASS")
    bundle = KnowledgeBundle(query=topic, items=items)
    context = bundle.context()

    print("[03/07] Initialize Generator             PASS")
    generator = ContentGenerator()

    print("[04/07] Generate Content                 PASS")
    files = {
        "facebook.docx": generator.generate_facebook(topic, context),
        "tiktok.docx": generator.generate_tiktok(topic, context),
        "image_prompt.docx": generator.generate_image_prompt(topic, context),
        "video_prompt.docx": generator.generate_video_prompt(topic, context),
        "seo.docx": generator.generate_seo(topic, context),
        "hashtags.docx": generator.generate_hashtags(),
        "approval_checklist.docx": generator.generate_checklist(),
    }

    print("[05/07] Prepare Output Folder            PASS")
    output_dir = OUTPUT_ROOT / f"Day{day:03d}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[06/07] Export DOCX                      PASS")
    exporter = DocxExporter()
    for filename, content in files.items():
        exporter.save(output_dir / filename, topic, content)

    print("[07/07] Production Completed             PASS")
    print("-" * 60)
    print("STATUS    : PRODUCTION SUCCESS")
    print(f"Knowledge : {len(items)} item(s)")
    print(f"Output    : {output_dir}")

    import subprocess

    if sys.platform == "darwin":
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
