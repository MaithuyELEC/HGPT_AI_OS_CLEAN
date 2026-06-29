from abc import ABC, abstractmethod

class BaseAgent(ABC):

    @abstractmethod
    def run(self):
        """Execute the agent."""
        raise NotImplementedError
