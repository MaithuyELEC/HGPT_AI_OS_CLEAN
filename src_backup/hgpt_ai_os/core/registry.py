class Registry:

    def __init__(self):
        self.agents = {}
        self.workflows = {}

    def register_agent(self, name, agent):
        self.agents[name] = agent

    def register_workflow(self, name, workflow):
        self.workflows[name] = workflow

    def get_agent(self, name):
        return self.agents.get(name)

    def get_workflow(self, name):
        return self.workflows.get(name)
