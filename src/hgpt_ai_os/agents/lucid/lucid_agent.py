from hgpt_ai_os.orchestrator.lucid_orchestrator import LucidOrchestrator


class LucidAgent:

    def run(self):
        print("=" * 60)
        print("HGPT LUCID AUTO")
        print("=" * 60)

        LucidOrchestrator().run()
