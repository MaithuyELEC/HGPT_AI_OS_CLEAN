from hgpt_ai_os.agents.marketing.marketing_agent import MarketingAgent


class MarketingWorkflow:

    def run(self, day=None):
        agent = MarketingAgent()

        if str(day) == "11":
            return agent.create_day11_content()

        raise NotImplementedError(
            f"Marketing Day {day} chưa được hỗ trợ."
        )