"""Knowledge Provider for ContentContext.

Handles retrieved context and default fallback logic.
Separates knowledge retrieval concerns from ContentContext creation.
"""


class KnowledgeProvider:
    """
    Provider for already retrieved context with fallback defaults.

    Content builders are legacy compatibility APIs. They must consume context
    supplied by the canonical retrieval pipeline, not read knowledge files.
    """

    def get_problem(self, topic: str, context: str) -> str:
        """
        Get problem statement with fallback.

        Returns context if provided and non-empty, otherwise returns
        a default problem statement based on the topic.

        Args:
            topic: Topic/title for fallback message
            context: Provided context from the retrieval pipeline

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
        return "Phân tích theo hiện tượng, nguyên nhân gốc, rủi ro và hành động kiểm soát."

    def get_solution(self) -> str:
        return "Chuẩn hóa quy trình, SOP và Knowledge Base."

    def get_lesson(self) -> str:
        return "Đừng chỉ sửa lỗi. Hãy sửa quy trình tạo ra lỗi."

    def get_cta(self) -> str:
        return "Theo dõi LUCID AUTO để chuẩn hóa sản xuất và kiểm soát chất lượng tốt hơn."

    def get_hashtags(self) -> list[str]:
        return [
            "#LUCIDAUTO",
            "#SteelFabrication",
            "#QAQC",
            "#ConstructionEngineering",
        ]
