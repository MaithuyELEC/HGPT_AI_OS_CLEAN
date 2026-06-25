from .engine import ContentContextEngine


class ContentContextBuilder:

    def __init__(self):
        self._engine = ContentContextEngine()

    def build(self, topic: str, context: str = ""):
        return self._engine.build(topic, context)
