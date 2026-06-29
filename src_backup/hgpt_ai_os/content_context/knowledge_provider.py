"""Knowledge Provider for ContentContext.

Handles knowledge loading and default fallback logic.
Separates knowledge retrieval concerns from ContentContext creation.
"""

from hgpt_ai_os.content.knowledge_loader import KnowledgeLoader


class KnowledgeProvider:
    """
    Provider for knowledge content with fallback defaults.
    
    Manages knowledge loading from files and provides sensible defaults
    when content is missing or empty. Implements the knowledge loading
    responsibility previously mixed into ContentContextEngine.
    
    This component encapsulates:
    - Loading knowledge from files via KnowledgeLoader
    - Applying default fallbacks for missing content
    - Sanitizing and normalizing loaded content
    """
    
    def __init__(self):
        """Initialize provider with KnowledgeLoader dependency."""
        self._loader = KnowledgeLoader()
    
    def get_problem(self, topic: str, context: str) -> str:
        """
        Get problem statement with fallback.
        
        Returns context if provided and non-empty, otherwise returns
        a default problem statement based on the topic.
        
        Args:
            topic: Topic/title for fallback message
            context: Provided context (usually from knowledge bundle)
        
        Returns:
            Problem statement string
        """
        if context and context.strip():
            return context.strip()
        
        return (
            f"Trong quá trình {topic}, nếu chỉ xử lý hiện tượng "
            "mà không tìm nguyên nhân gốc thì lỗi sẽ tiếp tục tái diễn."
        )
    
    def get_framework(self) -> str:
        """
        Load framework/analysis content.
        
        Returns:
            Framework content from facebook/framework.md
        """
        return self._loader.load("facebook/framework.md")
    
    def get_solution(self) -> str:
        """
        Get solution content with fallback.
        
        Returns:
            Solution from facebook/solution.md or default if missing
        """
        content = self._loader.load("facebook/solution.md")
        if content and content.strip():
            return content
        
        return "Chuẩn hóa quy trình, SOP và Knowledge Base."
    
    def get_lesson(self) -> str:
        """
        Get lesson content with fallback.
        
        Returns:
            Lesson from facebook/lesson.md or default if missing
        """
        content = self._loader.load("facebook/lesson.md")
        if content and content.strip():
            return content
        
        return "Đừng chỉ sửa lỗi. Hãy sửa quy trình tạo ra lỗi."
    
    def get_cta(self) -> str:
        """
        Load call-to-action content.
        
        Returns:
            CTA from facebook/cta.md
        """
        return self._loader.load("facebook/cta.md")
    
    def get_hashtags(self) -> list[str]:
        """
        Load hashtags from default collection.
        
        Returns:
            List of hashtags from hashtags/default.txt
        """
        content = self._loader.load("hashtags/default.txt")
        return content.splitlines() if content else []
