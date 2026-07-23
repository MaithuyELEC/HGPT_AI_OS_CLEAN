from __future__ import annotations

import ast
import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

from hgpt_ai_os.content_brain.facebook_brain import render_facebook_content as render_facebook_brain
from hgpt_ai_os.content_brain.image_brain import render_image_prompt as render_image_brain
from hgpt_ai_os.content_brain.video_brain import render_video_prompt as render_video_brain
from hgpt_ai_os.content.prompt_libraries import CAMERA_LIBRARY, LIGHTING_LIBRARY, VOICE_LIBRARY, choose

from .record import EngineeringRecord


_FIELD_LABELS = {
    "cause": "Nguyên nhân",
    "category": "Nhóm lỗi",
    "symptoms": "Dấu hiệu",
    "failure_symptom": "Dấu hiệu",
    "mechanism": "Cơ chế hư hỏng",
    "physical_mechanism": "Cơ chế hư hỏng",
    "inspection": "Cách kiểm tra",
    "inspection_method": "Cách kiểm tra",
    "measurements": "Đo kiểm",
    "measurement": "Đo kiểm",
    "tools": "Dụng cụ",
    "instruments": "Dụng cụ",
    "expected_values": "Giá trị đối chiếu",
    "decision_logic": "Logic quyết định",
    "repair": "Cách xử lý",
    "repair_procedure": "Cách xử lý",
    "verification": "Xác nhận sau sửa",
    "acceptance": "Tiêu chí bàn giao",
    "acceptance_criteria": "Tiêu chí bàn giao",
    "prevention": "Phòng ngừa",
    "preventive_maintenance": "Phòng ngừa",
}

_INTERNAL_KEYS = {
    "failure_modes",
    "root_causes",
    "recommended_actions",
    "inspection_steps",
    "preventive_actions",
    "safety_notes",
    "tools_required",
    "source_keys",
    "confidence",
}

_ALLOWED_ENGLISH_TERMS = {
    "ISO",
    "IEC",
    "AWS",
    "API",
    "LOTO",
    "NDT",
    "VFD",
    "OEM",
    "QA",
    "QC",
    "CMMS",
    "SCADA",
}

_ENGLISH_LEAKAGE_TERMS = {
    "provider",
    "prompt",
    "json",
    "dict",
    "list",
    "repr",
    "generic",
    "management",
    "marketing",
    "facebook",
    "tiktok",
    "hashtag",
    "blog",
    "chatgpt",
}

_GENERIC_FIELD_FALLBACKS = {
    "domain": "Bảo trì kỹ thuật",
    "title": "Hồ sơ xử lý sự cố kỹ thuật",
    "problem": "Sự cố cần được xác nhận bằng dữ liệu hiện trường trước khi kết luận.",
    "equipment": "thiết bị/khu vực theo hồ sơ kỹ thuật",
    "subsystem": "cụm chức năng cần kiểm tra",
    "component": "chi tiết liên quan cần xác nhận",
    "failure_symptom": "triệu chứng bất thường cần ghi nhận tại hiện trường",
    "operating_context": "bối cảnh vận hành cần được mô tả bằng dữ liệu hiện trường.",
    "working_principle": "nguyên lý làm việc cần được đối chiếu với tài liệu kỹ thuật.",
    "failure_mechanisms": "cơ chế hư hỏng cần được xác nhận bằng kiểm tra và đo kiểm.",
    "root_causes": "nguyên nhân gốc cần được khoanh vùng bằng bằng chứng đo kiểm.",
    "evidence_required": "bằng chứng hiện trường trước và sau sửa",
    "inspection_procedure": "kiểm tra hiện trường theo phiếu kiểm đã phê duyệt",
    "measurements": "thông số đo cần ghi lại trước và sau sửa",
    "tools_required": "dụng cụ đo kiểm phù hợp với thiết bị",
    "decision_logic": "nếu dữ liệu đo chưa đủ thì chưa kết luận nguyên nhân.",
    "repair_procedure": "thực hiện sửa chữa theo kết quả kiểm tra và hướng dẫn kỹ thuật.",
    "verification": "xác nhận sau sửa bằng cùng phương pháp đo kiểm ban đầu.",
    "acceptance_criteria": "chỉ bàn giao khi có đủ bằng chứng đạt yêu cầu.",
    "lessons_learned": "chuyển sự cố thành điểm kiểm soát trong bảo trì định kỳ.",
    "common_mistakes": "không kết luận khi thiếu dữ liệu đo kiểm.",
    "preventive_maintenance": "cập nhật kế hoạch bảo trì dựa trên bằng chứng lỗi.",
    "safety_controls": "cô lập năng lượng và kiểm soát an toàn trước khi thao tác.",
    "kaizen": "chuẩn hóa điểm đo và biểu mẫu ghi nhận cho lần kiểm tra sau.",
    "digital_factory_recommendations": "lưu dữ liệu đo, ảnh hiện trường và kết luận vào hệ thống quản lý bảo trì.",
    "applicable_standards": "chỉ sử dụng tiêu chuẩn đã được xác nhận.",
    "missing_information": "Không đủ dữ liệu để kết luận. Cần đo và bổ sung bằng chứng hiện trường.",
}

_GENERIC_TERM_REPLACEMENTS = (
    ("Root Cause Analysis", "Phân tích nguyên nhân gốc"),
    ("root cause analysis", "phân tích nguyên nhân gốc"),
    ("Root Causes", "Nguyên nhân gốc"),
    ("Root causes", "Nguyên nhân gốc"),
    ("root causes", "nguyên nhân gốc"),
    ("Root cause", "Nguyên nhân gốc"),
    ("root cause", "nguyên nhân gốc"),
    ("Practical solution", "Cách xử lý thực tế"),
    ("Real shop scenario", "Tình huống hiện trường"),
    ("Lesson learned", "Bài học rút ra"),
    ("Call To Action", "Câu hỏi thảo luận"),
    ("Inspection", "Kiểm tra"),
    ("inspection", "kiểm tra"),
    ("Repair", "Sửa chữa"),
    ("repair", "sửa chữa"),
    ("Acceptance", "Nghiệm thu"),
    ("acceptance", "nghiệm thu"),
    ("Prevention", "Phòng ngừa"),
    ("prevention", "phòng ngừa"),
    ("Workflow", "Quy trình"),
    ("workflow", "quy trình"),
    ("Summary", "Tóm tắt"),
    ("article", "bài viết"),
    ("search keywords", "từ khóa tìm kiếm"),
    ("keyword", "từ khóa"),
    ("release", "bàn giao"),
    ("pass/fail", "đạt/không đạt"),
    ("hold point", "điểm dừng kiểm soát"),
    ("AI provider", "nguồn dữ liệu kỹ thuật"),
    ("AI Provider", "nguồn dữ liệu kỹ thuật"),
    ("provider", "nguồn dữ liệu"),
    ("Maintenance", "Bảo trì"),
    ("maintenance", "bảo trì"),
    ("Checklist", "Phiếu kiểm"),
    ("checklist", "phiếu kiểm"),
    ("OEM manual", "tài liệu hãng sản xuất"),
    ("OEM", "hãng sản xuất"),
    ("QA/QC", "kiểm soát chất lượng"),
    ("CMMS", "hệ thống quản lý bảo trì"),
    ("SCADA", "hệ thống giám sát điều khiển"),
    ("Digital Factory", "Nhà máy số"),
    ("digital factory", "nhà máy số"),
    ("measured in", "đơn vị"),
    ("post-repair", "sau sửa"),
)


def render_all(record: EngineeringRecord) -> dict[str, str]:
    rendered = _RenderedRecord(record)
    content = ContentTransformation.from_record(rendered)
    return {
        "facebook.docx": render_facebook(content),
        "tiktok.docx": render_tiktok(content),
        "image_prompt.docx": render_image_prompt(content),
        "video_prompt.docx": render_video_prompt(content),
        "seo.docx": render_seo(content),
        "hashtags.docx": render_hashtags(content),
        "approval_checklist.docx": render_checklist(content),
    }


@dataclass(frozen=True)
class ContentTransformation:
    topic: str
    pain_points: tuple[str, ...]
    shop_story: str
    root_causes: tuple[str, ...]
    inspection_steps: tuple[str, ...]
    repair_steps: tuple[str, ...]
    acceptance: tuple[str, ...]
    prevention: tuple[str, ...]
    lesson_learned: tuple[str, ...]
    cta: str
    seo_keywords: tuple[str, ...]
    visual_subject: str
    visual_scene: str
    camera: str
    lighting: str
    composition: str
    video_storyboard: tuple[str, ...]
    voice: str
    ambient: str
    emotion: str
    equipment: str
    component: str
    working_principle: str
    visual_materials: str
    visual_motion: str
    visual_negative_prompt: str

    @classmethod
    def from_record(cls, record: "_RenderedRecord") -> "ContentTransformation":
        topic = _content_text(record.topic, "sự cố kỹ thuật trong xưởng")
        equipment = _content_text(_join(record.equipment[:4], record.main_entity or topic), topic)
        component = _content_text(_join(record.component[:4], "cụm chi tiết liên quan"), "cụm chi tiết liên quan")
        pain_points = _content_items(record.failure_symptom, record.problem, 4)
        root_causes = _content_items(record.root_causes or record.failure_mechanisms, record.problem, 5)
        inspection_steps = _content_items(record.inspection_procedure, "ghi nhận hiện trạng và kiểm tra tại điểm lỗi", 6)
        repair_steps = _content_items(record.repair_procedure, "sửa đúng nguyên nhân đã xác nhận", 5)
        acceptance = _content_items(record.acceptance_criteria or record.verification, "chạy thử ổn định và ghi kết quả sau sửa", 5)
        prevention = _content_items(record.preventive_maintenance or record.kaizen, "đưa dấu hiệu sớm vào lịch kiểm tra định kỳ", 6)
        lesson_learned = _content_items(record.lessons_learned, "khóa nguyên nhân bằng dữ liệu trước khi bàn giao", 4)
        keywords = tuple(dict.fromkeys(_items((topic, record.domain, record.topic_type, equipment, component), limit=8)))
        symptoms = _join(pain_points[:3], topic)
        shop_story = (
            f"Ca sản xuất đang chạy, {equipment} bắt đầu xuất hiện {symptoms.lower()}. "
            "Tổ vận hành muốn xử lý thật nhanh, nhưng trưởng ca giữ hiện trạng, ghi dấu vết, đo lại điểm nghi ngờ và chỉ cho sửa khi nguyên nhân đã rõ."
        )
        visual_subject = f"kỹ sư bảo trì hoặc QA/QC Việt Nam kiểm tra {component}"
        visual_scene = f"xưởng kết cấu thép với {equipment}, khu vực được cô lập an toàn, dấu vết lỗi nhìn rõ"
        storyboard = (
            f"Mở đầu: dừng nhịp sản xuất khi thấy {symptoms.lower()} trên {equipment}.",
            f"Biểu hiện lỗi: máy hoặc cụm chi tiết bộc lộ dấu hiệu bất thường tại {component}.",
            f"Chẩn đoán: đội kỹ thuật kiểm tra {', '.join(inspection_steps[:3])}.",
            f"Khắc phục: thực hiện {', '.join(repair_steps[:3])} theo nguyên nhân đã xác nhận.",
            f"Xác nhận: xác nhận {', '.join(acceptance[:3])} trước khi bàn giao.",
            f"Kết thúc: lưu bài học {', '.join(lesson_learned[:2])} để ca sau không lặp lỗi.",
        )
        return cls(
            topic=topic,
            pain_points=pain_points,
            shop_story=shop_story,
            root_causes=root_causes,
            inspection_steps=inspection_steps,
            repair_steps=repair_steps,
            acceptance=acceptance,
            prevention=prevention,
            lesson_learned=lesson_learned,
            cta=f"Bạn sẽ kiểm điểm nào đầu tiên khi gặp {topic.lower()} trong ca thật?",
            seo_keywords=keywords,
            visual_subject=visual_subject,
            visual_scene=visual_scene,
            camera=choose(CAMERA_LIBRARY, f"ct:{topic}:{equipment}"),
            lighting=choose(LIGHTING_LIBRARY, f"ct:{topic}:{equipment}", 1),
            composition="rule of thirds, foreground tool, middle-ground evidence, background production line, clear handover space",
            video_storyboard=storyboard,
            voice=choose(VOICE_LIBRARY, f"ct:{topic}:{equipment}", 2),
            ambient="factory ambience, gauge beep, ventilation, restrained machine hum, pen mark on checklist",
            emotion="focused, disciplined, calm under production pressure",
            equipment=equipment,
            component=component,
            working_principle=_content_text(record.working_principle, "thiết bị phải làm việc đúng tải, đúng căn chỉnh và đúng điều kiện vận hành"),
            visual_materials="painted steel, scratched bare metal, weld beads, bolts, hoses, gauges, LOTO tag, paper checklist, worn concrete",
            visual_motion="operator pauses, engineer measures, supervisor confirms, team steps back before restart",
            visual_negative_prompt="no unsafe action, no missing PPE, no fake text, no watermark, no cartoon, no unrelated equipment, no disaster scene",
        )


@dataclass(frozen=True)
class BrainTopicAdapter:
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

    @classmethod
    def from_content(cls, content: ContentTransformation) -> "BrainTopicAdapter":
        return cls(
            topic=content.topic,
            domain=content.equipment,
            subject=content.component,
            problem=content.working_principle,
            objects=_ensure_items((content.equipment, content.component, *content.seo_keywords), 5),
            risks=_ensure_items(content.acceptance, 4),
            causes=_ensure_items(content.root_causes, 5),
            actions=_ensure_items(content.prevention, 6),
            signs=_ensure_items(content.pain_points, 3),
            hashtags=_facebook_hashtags(content),
        )


def render_facebook(content: ContentTransformation) -> str:
    topic = BrainTopicAdapter.from_content(content)
    return render_facebook_brain(topic, list(topic.hashtags))


def render_tiktok(content: ContentTransformation) -> str:
    return "\n".join(
        [
            f"Mở đầu - {content.topic}",
            f"Nỗi đau hiện trường - {_join(content.pain_points[:2], content.topic)}.",
            f"Câu chuyện trong xưởng - {content.shop_story}",
            f"Nguyên nhân gốc - {_join(content.root_causes[:2], 'điều kiện tạo lỗi chưa bị khóa')}.",
            f"Hành động sửa - {_join(content.repair_steps[:3], 'sửa theo nguyên nhân đã xác nhận')}.",
            f"Xác nhận sau sửa - {_join(content.acceptance[:2], 'kiểm tra lại trước bàn giao')}.",
            f"Kết thúc thảo luận - {content.cta}",
        ]
    )


def render_image_prompt(content: ContentTransformation) -> str:
    return render_image_brain(BrainTopicAdapter.from_content(content))


def render_video_prompt(content: ContentTransformation) -> str:
    return render_video_brain(BrainTopicAdapter.from_content(content))


def render_seo(content: ContentTransformation) -> str:
    slug = _slug(content.topic)
    return "\n".join(
        [
            f"H1: {content.topic}: nguyên nhân, kiểm tra, sửa chữa và phòng ngừa",
            "",
            "Mở đầu",
            (
                f"{content.topic} là một truy vấn kỹ thuật quan trọng vì nó ảnh hưởng trực tiếp đến an toàn, chất lượng và tiến độ trong xưởng. "
                f"Khi người vận hành hoặc QA/QC thấy {_join(content.pain_points[:3], content.topic).lower()}, câu hỏi không chỉ là sửa gì cho nhanh. "
                "Câu hỏi đúng là nguyên nhân nào tạo ra lỗi, kiểm tra bằng chứng ra sao, điều kiện nào được chấp nhận, và phòng ngừa thế nào để lỗi không quay lại."
            ),
            (
                f"Bài viết này chuyển tri thức kỹ thuật thành nội dung dễ tra cứu cho kỹ sư, tổ bảo trì và quản lý ca. "
                f"Nội dung dùng các từ khóa tự nhiên như {', '.join(content.seo_keywords[:5])}, nguyên nhân gốc, kiểm tra, sửa chữa, nghiệm thu, phòng ngừa và {slug}. "
                "Mục tiêu là giúp người đọc hiểu đúng việc cần làm trước khi chạm vào thiết bị hoặc ký nghiệm thu."
            ),
            "",
            "H2: Nguyên nhân gốc",
            (
                f"Dấu hiệu thường gặp gồm {_join(content.pain_points[:4], content.topic)}. "
                f"Các dấu hiệu này liên quan đến {content.equipment} và {content.component}. "
                "Không nên kết luận chỉ bằng một quan sát, vì cùng một triệu chứng có thể đến từ nhiều điều kiện khác nhau."
            ),
            (
                f"Về cơ chế, {content.working_principle}. "
                "Nguyên nhân gốc chỉ đủ mạnh khi có bằng chứng quan sát, kết quả ghi nhận và xác nhận sau sửa."
            ),
            *_bullets(content.root_causes, 6),
            "",
            "H2: Kiểm tra",
            (
                "Kiểm tra phải được thực hiện trước khi sửa để không xóa mất dấu vết hiện trường. "
                "Đội kỹ thuật cần ghi vị trí lỗi, điều kiện vận hành, ảnh hiện trường, thông số đo và người xác nhận. "
                "Nếu thiếu dữ liệu, phải giữ trạng thái giả thuyết thay vì biến giả thuyết thành kết luận."
            ),
            *_bullets(content.inspection_steps, 8),
            "",
            "H2: Sửa chữa",
            (
                "Sửa chữa phải đi sau nguyên nhân gốc. Nếu chỉ xử lý phần dễ thấy nhất, lỗi có thể biến mất trong vài giờ rồi quay lại khi tải, nhiệt, rung, áp suất hoặc điều kiện công đoạn thay đổi. "
                "Quy trình sửa đúng cần loại bỏ điều kiện tạo lỗi, không chỉ làm đẹp triệu chứng."
            ),
            *_bullets(content.repair_steps, 8),
            "",
            "H2: Nghiệm thu",
            (
                f"Nghiệm thu là điểm phân biệt sửa xong và sửa đúng. Với {content.topic}, nghiệm thu cần dựa trên bằng chứng trước/sau, tiêu chí đạt/không đạt, người xác nhận, và điều kiện vận hành khi kiểm tra lại."
            ),
            *_bullets(content.acceptance, 8),
            "",
            "H2: Phòng ngừa",
            (
                f"Phòng ngừa cho {content.topic} nên biến bài học thành phiếu kiểm, lịch bảo trì, điểm dừng kiểm soát, SOP hoặc điểm kiểm trong ITP. "
                "Nếu lỗi đã xảy ra một lần, hệ thống phải giúp người sau nhận diện sớm hơn."
            ),
            *_bullets(content.prevention, 7),
            *_bullets(content.lesson_learned, 4),
            (
                f"Với {content.topic}, dữ liệu nên được lưu theo ba nhóm: dấu hiệu phát hiện, phép kiểm hoặc phép đo, và kết quả sau sửa. "
                "Ba nhóm này giúp bài viết không chỉ có từ khóa mà còn có khả năng hướng dẫn thực tế cho người tìm kiếm."
            ),
            "",
            "Câu hỏi thường gặp",
            f"Hỏi: Dấu hiệu nào cho thấy cần ưu tiên {content.topic}?\nĐáp: Khi xuất hiện {_join(content.pain_points[:3], content.topic)}, đặc biệt nếu lỗi lặp lại ở cùng thiết bị, công đoạn hoặc điều kiện vận hành.",
            f"Hỏi: Kiểm tra đầu tiên nên làm gì?\nĐáp: Ghi hiện trạng, cô lập rủi ro nếu cần, sau đó kiểm {_join(content.inspection_steps[:2], 'điểm kiểm tra chính')}.",
            f"Hỏi: Sửa chữa có thể làm ngay không?\nĐáp: Có thể kiểm soát an toàn ngay, nhưng sửa chữa chính thức nên đi sau bằng chứng nguyên nhân gốc để tránh sửa sai điểm tạo lỗi.",
            f"Hỏi: Nghiệm thu cần gì?\nĐáp: Cần {_join(content.acceptance[:3], 'kết quả trước/sau, tiêu chí đạt/không đạt và người xác nhận')}.",
            f"Hỏi: Làm sao phòng ngừa hiệu quả hơn?\nĐáp: Đưa {_join(content.lesson_learned[:2], 'bài học sau sửa')} vào phiếu kiểm, lịch kiểm tra hoặc SOP ca sau.",
            "",
            "Tóm tắt",
            (
                f"{content.topic} cần được xử lý như một chuỗi hoàn chỉnh: nguyên nhân gốc, kiểm tra, sửa chữa, nghiệm thu và phòng ngừa. "
                "Khi đội hiện trường giữ đúng chuỗi này, tri thức nguồn được chuyển thành hướng dẫn tìm kiếm, đọc hiểu và áp dụng trong ca sản xuất."
            ),
            "",
        ]
    )


def render_checklist(content: ContentTransformation) -> str:
    return "\n".join(
        [
            "## Phiếu kiểm phê duyệt kỹ thuật",
            "",
            "### Thông tin đầu vào",
            f"- Chủ đề: {content.topic}",
            f"- Thiết bị/khu vực: {content.equipment}",
            "",
            "### Kiểm tra bắt buộc",
            *_checkboxes(content.inspection_steps, 8),
            "",
            "### Quyết định sửa chữa",
            *_checkboxes(content.root_causes, 5),
            *_checkboxes(content.repair_steps, 6),
            "",
            "### Xác nhận sau sửa",
            *_checkboxes(content.acceptance, 6),
            "",
            "### Không được quên",
            *_checkboxes(content.prevention, 4),
            *_checkboxes(content.lesson_learned, 4),
        ]
    )


def render_hashtags(content: ContentTransformation) -> str:
    return "\n".join(_facebook_hashtags(content))


def _facebook_hashtags(content: ContentTransformation) -> tuple[str, ...]:
    normalized = _ascii_words(content.topic)
    if "saw" in normalized or "han" in normalized or "weld" in normalized:
        base = (
            "#LucidAIStudio",
            "#HGPTSteel",
            "#KetCauThep",
            "#Welding",
            "#SAW",
            "#QAQC",
            "#NDT",
            "#UT",
            "#RT",
            "#WPS",
        )
    elif "cau truc" in normalized or "phanh" in normalized or "crane" in normalized:
        base = ("#LucidAIStudio", "#HGPTSteel", "#CauTruc", "#BaoTri", "#ThietBiNang", "#AnToanNangHa")
    elif "son" in normalized or "paint" in normalized or "coating" in normalized:
        base = ("#LucidAIStudio", "#HGPTSteel", "#SonPhu", "#KetCauThep", "#QAQC", "#DFT")
    elif "vong bi" in normalized or "bearing" in normalized:
        base = ("#LucidAIStudio", "#HGPTSteel", "#BaoTri", "#DongCo", "#VongBi", "#BaoTriPhongNgua")
    else:
        base = ("#LucidAIStudio", "#HGPTSteel", "#KetCauThep", "#KienThucXuong")
    topic_tags = tuple(_hashtag(value) for value in (content.topic, content.equipment, content.component))
    tags: list[str] = []
    for tag in (*base, *topic_tags):
        if tag and tag not in tags:
            tags.append(tag)
    return tuple(tags[:12])
    return "\n".join(
        [
            "## Thẻ phân loại kiến thức",
            "",
            *_bullets(tuple(tag for tag in tags if tag), 16),
        ]
    )


def _bullets(values: tuple[str, ...], limit: int) -> list[str]:
    return [f"- {value}" for value in values[:limit] if value]


def _checkboxes(values: tuple[str, ...], limit: int) -> list[str]:
    return [f"- ☐ {value}" for value in values[:limit] if value]


def _first(values: tuple[str, ...], fallback: str) -> str:
    return values[0] if values else fallback


def _join(values: tuple[str, ...], fallback: str) -> str:
    cleaned = [value for value in values if value]
    return ", ".join(cleaned) if cleaned else fallback


def _visual_join(values: tuple[str, ...], fallback: str) -> str:
    cleaned = [_visual_text(value, "") for value in values]
    cleaned = [value for value in cleaned if value]
    return ", ".join(cleaned) if cleaned else fallback


def _visual_text(value: str, fallback: str) -> str:
    text = (value or "").strip()
    if not text:
        return fallback
    lowered = text.lower()
    blocked = (
        "không đủ dữ liệu",
        "chưa đủ bằng chứng",
        "không sử dụng",
        "missing data",
        "unsupported numeric",
        "engineeringrecord",
        "internal system",
    )
    if any(term in lowered for term in blocked):
        return fallback
    return text


_FORBIDDEN_CONTENT_TERMS = (
    "Đây là gì",
    "Vì sao xảy ra",
    "Thông tin còn thiếu",
    "Cần bằng chứng",
    "Engineering Record",
    "EngineeringRecord",
    "Mục lục tra cứu",
    "Cấu trúc hồ sơ",
    "Trích yếu",
    "Đo kiểm",
    "Tiêu chuẩn",
    "condition requires field confirmation",
)

_INTERNAL_ENUM_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b")

_SOURCE_LABEL_PATTERNS = (
    r"\bHạng\s+\d+\s*-\s*",
    r"\bVì sao xảy ra\s*:\s*",
    r"\bCơ chế vật lý\s*:\s*",
    r"\bCơ chế hoạt động hoặc cơ chế lỗi\s*:\s*",
    r"\bKiểm tra\s*:\s*",
    r"\bĐo kiểm\s*:\s*",
    r"\bDụng cụ\s*:\s*",
    r"\bLogic quyết định\s*:\s*",
    r"\bSửa chữa\s*:\s*",
    r"\bXác nhận\s*:\s*",
    r"\bTiêu chí nhận\s*:\s*",
    r"\bTiêu chuẩn\s*:\s*",
)


def _content_items(values: tuple[str, ...], fallback: str, limit: int) -> tuple[str, ...]:
    cleaned = tuple(_content_text(value, "") for value in values)
    cleaned = tuple(value for value in cleaned if value)
    if not cleaned:
        cleaned = (_content_text(fallback, "điểm kỹ thuật cần xác nhận tại hiện trường"),)
    return tuple(dict.fromkeys(cleaned))[:limit]


def _content_text(value: str, fallback: str) -> str:
    text = _clean_text(value or "")
    for pattern in _SOURCE_LABEL_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bhồ sơ kỹ thuật(?: nguồn)?\b", "tri thức hiện trường", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKhông đủ dữ liệu để kết luận\.?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCần đo(?: và bổ sung)?\b", "nên ghi", text, flags=re.IGNORECASE)
    for term in _FORBIDDEN_CONTENT_TERMS:
        text = re.sub(re.escape(term), "", text, flags=re.IGNORECASE)
    text = _INTERNAL_ENUM_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip(" ;,.:-")
    return text or fallback


def _slug(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", _ascii_words(value))
    return "-".join(words[:8]) or "engineering-record"


def _hashtag(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", _ascii_words(value))
    if not words:
        return ""
    return "#" + "".join(word.capitalize() for word in words[:5])


def _ascii_words(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _generic_fallback(field: str) -> str:
    return _GENERIC_FIELD_FALLBACKS.get(field, "")


def _has_unapproved_english(text: str) -> bool:
    for word in re.findall(r"\b[A-Za-z]{3,}\b", text):
        normalized = word.upper()
        if normalized in _ALLOWED_ENGLISH_TERMS:
            continue
        if word.lower() in _ENGLISH_LEAKAGE_TERMS:
            return True
    return False


class _RenderedRecord:
    _FIELDS = EngineeringRecord.__dataclass_fields__

    def __init__(self, record: EngineeringRecord) -> None:
        self._record = record

    def __getattr__(self, name: str):
        value = getattr(self._record, name)
        if name not in self._FIELDS:
            return value
        if isinstance(value, tuple):
            items = _items(value, field=name)
            return items
        if isinstance(value, str):
            text = _clean_text(value)
            return _generic_fallback(name) if _has_unapproved_english(text) else text
        return value


def _items(values: Iterable[object], limit: int | None = None, field: str = "") -> tuple[str, ...]:
    items: list[str] = []
    for value in values:
        items.extend(_flatten_value(value, field=field))
        if limit is not None and len(items) >= limit:
            break
    return tuple(dict.fromkeys(item for item in items if item))[:limit]


def _ensure_items(values: Iterable[object], size: int) -> tuple[str, ...]:
    fallback = (
        "ghi nhận hiện trạng bằng ảnh và điểm đo",
        "xác nhận điều kiện vận hành trước khi sửa",
        "đối chiếu kết quả với tiêu chí nghiệm thu",
        "phân người chịu trách nhiệm theo dõi sau bàn giao",
        "cập nhật checklist để ngăn lỗi lặp lại",
    )
    merged = _items((*values, *fallback), limit=size)
    return merged[:size]


def _flatten_value(value: object, field: str = "") -> list[str]:
    if value is None:
        return []
    parsed = _parse_structured_text(value) if isinstance(value, str) else value
    if parsed is None:
        return []
    if isinstance(parsed, dict):
        text = _render_mapping(parsed)
        return [text] if text else []
    if isinstance(parsed, (list, tuple, set)):
        items: list[str] = []
        for item in parsed:
            items.extend(_flatten_value(item, field=field))
        return items
    text = _clean_text(str(parsed))
    text = _INTERNAL_ENUM_RE.sub("", text).strip(" ;,.:-")
    for term in _FORBIDDEN_CONTENT_TERMS:
        text = re.sub(re.escape(term), "", text, flags=re.IGNORECASE).strip(" ;,.:-")
    if not text:
        return []
    if _has_unapproved_english(text):
        fallback = _generic_fallback(field)
        return [fallback] if fallback else []
    return [text]


def _render_mapping(values: dict[object, object]) -> str:
    parts: list[str] = []
    for raw_key, raw_value in values.items():
        key = _clean_key(raw_key)
        if not key or key in _INTERNAL_KEYS:
            continue
        label = _FIELD_LABELS.get(key)
        if not label:
            continue
        value = "; ".join(_flatten_value(raw_value, field=key))
        if value:
            parts.append(f"{label}: {value}")
    return ". ".join(parts)


def _parse_structured_text(value: str) -> object:
    text = value.strip()
    if not text:
        return None
    if text[:1] not in "{[":
        return text
    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(text)
        except (ValueError, SyntaxError, TypeError, json.JSONDecodeError):
            continue
    return text


def _clean_key(value: object) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(value).strip().lower()).strip("_")


def _clean_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if text[:1] in "{[":
        parsed = _parse_structured_text(text)
        if parsed is not text:
            return "; ".join(_flatten_value(parsed))
    text = _strip_internal_key_prefix(text)
    for source, target in sorted(_GENERIC_TERM_REPLACEMENTS, key=lambda item: len(item[0]), reverse=True):
        text = re.sub(re.escape(source), target, text, flags=re.IGNORECASE)
    text = re.sub(r"\bif\b", "nếu", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthen\b", "thì", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d+\.\s*", "", text)
    text = re.sub(r"\b(?:dict|list|repr|json\.dumps|str\s*\()\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ;,.")


def _strip_internal_key_prefix(text: str) -> str:
    key_match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.+)$", text)
    if not key_match:
        return text
    key = _clean_key(key_match.group(1))
    if key in _INTERNAL_KEYS or key in _FIELD_LABELS:
        return key_match.group(2).strip()
    return text
