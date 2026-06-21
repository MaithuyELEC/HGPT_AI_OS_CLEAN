from typing import Dict

from hgpt_ai_os.agents.base_agent import BaseAgent
from hgpt_ai_os.logger.logger import logger


class AgentManager:
    """HGPT AI OS Kernel - Agent Manager"""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, name: str, agent: BaseAgent):
        self._agents[name] = agent
        logger.info(f"Registered Agent: {name}")

    def unregister(self, name: str):
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered Agent: {name}")

    def get(self, name: str):
        return self._agents.get(name)

    def list_agents(self):
        return list(self._agents.keys())

    def run(self, name: str):
        agent = self.get(name)

        if not agent:
            logger.warning(f"Agent '{name}' not found.")
            return

        logger.info(f"Running Agent: {name}")
        return agent.run()

    def run_all(self):
        logger.info("Running all registered agents...")

        for name, agent in self._agents.items():
            logger.info(f"Running Agent: {name}")
            agent.run()
