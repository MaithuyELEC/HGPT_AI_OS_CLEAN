from src.hgpt_ai_os.knowledge.engine import KnowledgeEngine

engine = KnowledgeEngine()

doc = engine.get("CX001")

if doc is None:
    print("❌ Knowledge not found")
else:
    print("=" * 60)
    print("Knowledge Engine Smoke Test")
    print("=" * 60)
    print(f"ID       : {doc.id}")
    print(f"Title    : {doc.title}")
    print(f"Category : {doc.category}")
    print(f"Tags     : {', '.join(doc.tags)}")
    print("-" * 60)
    print(doc.content)
    print("=" * 60)
    print("✅ PASS")
