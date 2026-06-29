from hgpt_ai_os.content_context.models import ContentContext


class FacebookWriter:

    def write(self, ctx: ContentContext) -> ContentContext:

        topic = ctx.title

        ctx.problem = (
            f"{topic} không chỉ là một lỗi kỹ thuật. "
            "Nếu chỉ khắc phục hiện tượng mà không xử lý nguyên nhân gốc, "
            "lỗi sẽ tiếp tục lặp lại, làm tăng chi phí, chậm tiến độ và ảnh hưởng chất lượng."
        )

        ctx.analysis = [
            "Quan sát hiện trường và thu thập dữ liệu thực tế.",
            "Phân tích nguyên nhân gốc bằng 5 Why hoặc Fishbone.",
            "Đánh giá rủi ro về Chất lượng - Tiến độ - Chi phí - An toàn.",
            "Lựa chọn giải pháp có hiệu quả và dễ tiêu chuẩn hóa.",
            "Cập nhật SOP và Knowledge Base để ngăn tái diễn.",
        ]

        ctx.solution = (
            "Chuẩn hóa quy trình, Checklist, SOP và Knowledge Base "
            "để biến kinh nghiệm thành tài sản của doanh nghiệp."
        )

        ctx.lesson = (
            "Một lỗi được xử lý chỉ giải quyết hôm nay. "
            "Một quy trình được chuẩn hóa sẽ ngăn lỗi trong nhiều năm tới."
        )

        return ctx
