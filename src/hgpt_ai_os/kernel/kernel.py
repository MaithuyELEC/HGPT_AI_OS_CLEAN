from hgpt_ai_os.kernel.agent_manager import AgentManager
from hgpt_ai_os.kernel.registry import Registry
from hgpt_ai_os.kernel.service_container import ServiceContainer


class HGPTKernel:
    """HGPT AI OS Core Kernel"""

    def __init__(self):
        self.services = ServiceContainer()
        self.registry = Registry()
        self.agents = AgentManager()
