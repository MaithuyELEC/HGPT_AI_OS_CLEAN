from hgpt_ai_os.agents.maintenance.maintenance_agent import MaintenanceAgent
from hgpt_ai_os.kernel.kernel import HGPTKernel


kernel = HGPTKernel()

maintenance = MaintenanceAgent()

kernel.agents.register("maintenance", maintenance)

kernel.agents.run("maintenance")
