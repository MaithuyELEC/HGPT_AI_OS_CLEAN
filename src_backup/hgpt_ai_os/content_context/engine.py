"""ContentContext Engine.

Builds ContentContext with hook selection and knowledge management.
Follows Single Responsibility Principle through KnowledgeProvider.
"""

from hgpt_ai_os.content.hook_selector import HookSelector
from hgpt_ai_os.content_context.models import ContentContext
from hgpt_ai_os.content_context.knowledge_provider import KnowledgeProvider


class ContentContextEngine:
    """
    Engine for creating ContentContext with all required fields.
    
    Responsibilities:
    - Hook selection
    - ContentContext creation
    
    Delegates knowledge loading to KnowledgeProvider to maintain
    Single Responsibility Principle.
    
    Public API:
        build(topic: str, context: str = "") -> ContentContext
    """

    def __init__(self):
        """Initialize engine with dependencies."""
        self._selector = HookSelector()
        self._knowledge = KnowledgeProvider()

    def build(self, topic: str, context: str = "") -> ContentContext:
        """
        Build ContentContext for the given topic and context.
        
        Creates a complete ContentContext with all fields populated:
        - title: The topic passed in
        - hook: Selected by HookSelector
        - problem: From context or default fallback
        - analysis: Framework content from knowledge
        - solution: Solution content with fallback
        - lesson: Lesson content with fallback
        - action: CTA content from knowledge
        - hashtags: Default hashtags from knowledge
        - image_prompt: Generated from topic and problem
        - video_prompt: Generated from topic and problem
        - metadata: Empty dict (for future use)
        
        Args:
            topic: Content topic/title
            context: Knowledge context (usually from bundle)
        
        Returns:
            ContentContext with all fields populated
        """
        problem = self._knowledge.get_problem(topic, context)

        return ContentContext(
            title=topic,
            hook=self._selector.select(topic),
            problem=problem,
            analysis=self._knowledge.get_framework(),
            solution=self._knowledge.get_solution(),
            lesson=self._knowledge.get_lesson(),
            action=self._knowledge.get_cta(),
            hashtags=self._knowledge.get_hashtags(),
            image_prompt=f"""Create an ultra realistic industrial engineering photo.

Topic:
{topic}

Knowledge:
{problem}
""",
            video_prompt=f"""Create a 30-second industrial cinematic video.

Topic:
{topic}

Knowledge:
{problem}
""",
)
