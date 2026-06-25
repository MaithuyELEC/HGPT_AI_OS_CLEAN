from .engine import ContentContextEngine


class ContentContextBuilder:
    """Facade for building ContentContext."""

    def __init__(self):
        self._engine = ContentContextEngine()

    def build(self, **kwargs):
        return self._engine.create(**kwargs)
