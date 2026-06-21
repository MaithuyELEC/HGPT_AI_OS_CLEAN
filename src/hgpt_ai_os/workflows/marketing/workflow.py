from hgpt_ai_os.agents.marketing.marketing_agent import MarketingAgent


class MarketingWorkflow:

    def run(self):
        agent = MarketingAgent()
        return agent.create_day11_content()
