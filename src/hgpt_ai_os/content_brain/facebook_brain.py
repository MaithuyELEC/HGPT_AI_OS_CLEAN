from __future__ import annotations

from typing import Protocol


class FacebookTopic(Protocol):
    topic: str
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]
    hashtags: tuple[str, ...]


def render_facebook_content(topic: FacebookTopic, hashtags: list[str]) -> str:
    root_causes = _five(topic.causes, _fallback_causes(topic))
    consequences = _four(topic.risks, _fallback_consequences(topic))
    preventive_actions = _six(topic.actions, _fallback_actions(topic))
    title = _title(topic.topic)
    opening, explanation, warning, cta = _story_blocks(topic)

    return "\n".join(
        [
            title,
            "",
            opening,
            explanation,
            "",
            warning,
            "",
            "🔎 5 nguyên nhân gốc thường gặp:",
            *[
                f"{index}. {cause}."
                for index, cause in enumerate(root_causes, start=1)
            ],
            "",
            "⚠️ Hậu quả nếu bỏ qua:",
            *[
                f"{index}. {consequence}."
                for index, consequence in enumerate(consequences, start=1)
            ],
            "",
            "✅ Cách phòng ngừa trong sản xuất:",
            *[
                f"{index}. {action}."
                for index, action in enumerate(preventive_actions, start=1)
            ],
            "",
            (
                "💬 “Chất lượng không đến từ may mắn. Chất lượng đến từ quy trình, kỷ luật và trách nhiệm.”"
            ),
            "",
            cta,
            "",
            " ".join(hashtags),
        ]
    )


def _fallback_causes(topic: FacebookTopic) -> tuple[str, ...]:
    return (
        f"thiếu tiêu chí kiểm tra rõ cho {topic.objects[0]}",
        f"không ghi nhận đầy đủ dấu hiệu {topic.signs[0]} trước khi sửa",
        "trách nhiệm giữa vận hành, kỹ thuật và kiểm soát chất lượng chưa được khóa",
        "chỉ xử lý triệu chứng mà chưa xác nhận điều kiện gây lỗi",
        "không có bước xác nhận lại sau khắc phục",
    )


def _fallback_consequences(topic: FacebookTopic) -> tuple[str, ...]:
    return (
        topic.risks[0],
        topic.risks[1] if len(topic.risks) > 1 else "lỗi quay lại ở ca sau",
        topic.risks[2] if len(topic.risks) > 2 else "hồ sơ nghiệm thu thiếu bằng chứng",
        "đội hiện trường mất thời gian tranh luận thay vì xử lý theo dữ liệu",
    )


def _fallback_actions(topic: FacebookTopic) -> tuple[str, ...]:
    return (
        topic.actions[0],
        topic.actions[1] if len(topic.actions) > 1 else f"kiểm tra lại {topic.objects[0]} bằng tiêu chí rõ",
        topic.actions[2] if len(topic.actions) > 2 else "ghi nhận ảnh trước và sau khi xử lý",
        topic.actions[3] if len(topic.actions) > 3 else "phân người chịu trách nhiệm theo dõi trong ca kế tiếp",
        "kiểm tra chất lượng trong quá trình sản xuất trước khi chuyển công đoạn",
        "đưa dấu hiệu và nguyên nhân chính vào checklist phòng ngừa",
    )


def _five(values: tuple[str, ...], fallback: tuple[str, ...]) -> tuple[str, ...]:
    return _sized(values, fallback, 5)


def _six(values: tuple[str, ...], fallback: tuple[str, ...]) -> tuple[str, ...]:
    return _sized(values, fallback, 6)


def _four(values: tuple[str, ...], fallback: tuple[str, ...]) -> tuple[str, ...]:
    return _sized(values, fallback, 4)


def _sized(values: tuple[str, ...], fallback: tuple[str, ...], size: int) -> tuple[str, ...]:
    result: list[str] = []
    for value in (*values, *fallback):
        cleaned = value.strip().rstrip(".")
        if cleaned and cleaned not in result:
            result.append(cleaned)
        if len(result) == size:
            break
    return tuple(result)


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values)


def _story_blocks(topic: FacebookTopic) -> tuple[str, str, str, str]:
    if _is_saw(topic.topic):
        return (
            (
                f"Một đường hàn SAW nhìn đều, đẹp và bóng chưa chắc đã là một đường hàn đạt chất lượng. "
                f"Với {topic.topic}, điều đáng sợ nhất là lỗi có thể nằm ẩn bên trong mối hàn, chỉ lộ ra khi kiểm tra UT, RT hoặc khi cấu kiện đã bước vào giai đoạn nghiệm thu."
            ),
            (
                f"Rỗ khí là các khoang khí nhỏ bị giữ lại trong kim loại mối hàn hoặc xuất hiện trên bề mặt khi khí không thoát kịp trong quá trình đông đặc. "
                f"Nếu chỉ nhìn ngoại quan, đội sản xuất có thể bỏ qua {topic.signs[0]} hoặc đánh giá thấp nguy cơ thật sự của lỗi này."
            ),
            (
                f"Về kỹ thuật, {_sentence(topic.problem)} Khi các điều kiện như {_join(topic.objects[:4])} không được kiểm soát đồng bộ, "
                "khí sinh ra trong vùng hồ quang có thể bị mắc kẹt, tạo lỗ rỗ và làm suy giảm độ tin cậy của liên kết hàn.\n"
                "Đây không phải là lỗi thẩm mỹ. Đây là lỗi chất lượng có thể ảnh hưởng trực tiếp đến khả năng làm việc của kết cấu thép."
            ),
            (
                "👉 Anh em làm hàn, QA/QC, NDT và kết cấu thép đã từng gặp rỗ khí SAW trong sản xuất chưa? "
                "Hãy chia sẻ nguyên nhân thực tế và cách đội bạn kiểm soát lỗi này trong xưởng."
            ),
        )
    return (
        (
            f"Trong xưởng, {topic.topic} hiếm khi bắt đầu bằng một sự cố lớn. Nó thường bắt đầu từ một dấu hiệu nhỏ như {topic.signs[0]}, "
            "rồi âm thầm kéo theo rủi ro chất lượng, an toàn hoặc tiến độ nếu đội hiện trường xem nhẹ."
        ),
        (
            f"Về kỹ thuật, {_sentence(topic.problem)} Khi {topic.objects[0]} và {topic.objects[1]} không được kiểm soát đúng, "
            "một lỗi nhỏ có thể biến thành điểm dừng sản xuất, chi phí sửa chữa hoặc hồ sơ nghiệm thu bị giữ lại."
        ),
        (
            "Đây không phải là chuyện xử lý cho xong ca. Đây là bài toán kỷ luật quy trình: nhìn đúng dấu hiệu, khóa đúng nguyên nhân, "
            "làm đúng hành động phòng ngừa và xác nhận bằng bằng chứng trước khi bàn giao."
        ),
        (
            f"👉 Anh em sản xuất, bảo trì, QA/QC và quản lý xưởng đã từng gặp {topic.topic.lower()} chưa? "
            "Hãy chia sẻ nguyên nhân thực tế và cách đội bạn kiểm soát lỗi này."
        ),
    )


def _title(topic: str) -> str:
    normalized = _ascii(topic)
    if _is_saw(topic):
        return "🚨 ĐƯỜNG HÀN SAW BỊ RỖ KHÍ – NHỎ NHƯNG CÓ THỂ GÂY HẬU QUẢ LỚN!"
    return f"🚨 {topic.upper()} – NHỎ NHƯNG CÓ THỂ GÂY HẬU QUẢ LỚN!"


def _sentence(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _is_saw(topic: str) -> bool:
    normalized = _ascii(topic)
    return "duong han saw" in normalized and "ro khi" in normalized


def _ascii(value: str) -> str:
    import re
    import unicodedata

    decomposed = unicodedata.normalize("NFD", (value or "").lower())
    no_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    no_marks = no_marks.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", no_marks).strip()
