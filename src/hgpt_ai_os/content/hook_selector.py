import re


class HookSelector:

    RULES = [
        (r"\bQAQC\b", "Một lỗi nhỏ hôm nay có thể trở thành chi phí rất lớn ngày mai."),
        (r"\bKAIZEN\b", "Kaizen không phải làm nhiều hơn. Kaizen là làm thông minh hơn."),
        (r"\bMAINTENANCE\b", "Đừng chờ máy hỏng rồi mới bảo trì."),
        (r"\bDIGITAL\b", "Đây là cách tôi biến kinh nghiệm thành tri thức số."),
        (r"\bAI\b", "90% nhà máy đang làm sai điều này."),
    ]

    def select(self, topic: str):
        t = topic.upper()

        for pattern, hook in self.RULES:
            if re.search(pattern, t):
                return hook

        return "Bạn có đang mắc lỗi này mà không hề biết?"
