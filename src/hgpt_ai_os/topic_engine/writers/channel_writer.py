from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from hgpt_ai_os.diagnostics import fallback, instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.engineering_knowledge_library import EngineeringKnowledgeLibrary, EngineeringPlaybook
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject


@dataclass(frozen=True)
class DomainPlaybook:
    key: str
    aliases: tuple[str, ...]
    domain: str
    process: str
    equipment: str
    typical_symptoms: tuple[str, ...]
    technical_mechanism: str
    likely_causes: tuple[str, ...]
    inspection_steps: tuple[str, ...]
    corrective_actions: tuple[str, ...]
    preventive_actions: tuple[str, ...]
    safety_risks: tuple[str, ...]
    quality_risks: tuple[str, ...]
    production_impact: str
    checklist_items: tuple[str, ...]
    hashtags: tuple[str, ...]
    match_groups: tuple[tuple[str, ...], ...] = ()
    extra_corrective_actions: tuple[str, ...] = ()
    video_subject: str = ""
    failure_mechanisms: tuple[str, ...] = ()
    measurements: tuple[str, ...] = ()
    engineering_calculations: tuple[str, ...] = ()
    verification_steps: tuple[str, ...] = ()
    engineering_notes: tuple[str, ...] = ()
    common_mistakes: tuple[str, ...] = ()
    lessons_learned: tuple[str, ...] = ()
    standards: tuple[str, ...] = ()


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.lower())
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text).strip()


def _fallback_playbook(reasoning: ReasoningObject) -> DomainPlaybook:
    fallback("No matched domain playbook; using GENERAL_ENGINEERING fallback playbook.")
    topic = reasoning.topic.strip() or "vấn đề kỹ thuật hiện trường"
    inspections = (
        "kiểm tra trực quan tại khu vực liên quan",
        "ghi bằng chứng đo kiểm hoặc ảnh hiện trường",
        "đối chiếu tiêu chí nghiệm thu trước khi bàn giao",
        "xác nhận người chịu trách nhiệm và thời điểm kiểm tra",
    )
    actions = (
        "cô lập bất thường khỏi luồng bàn giao",
        "xác định nguyên nhân theo dữ liệu tại hiện trường",
        "sửa theo tiêu chí kỹ thuật đã thống nhất",
        "kiểm tra lại và lưu bằng chứng sau sửa",
    )
    return DomainPlaybook(
        key="GENERAL_ENGINEERING",
        aliases=(topic,),
        domain="Sản xuất cơ khí",
        process=topic,
        equipment="khu vực sản xuất liên quan",
        typical_symptoms=(
            f"dấu hiệu bất thường liên quan đến {topic}",
            "kết quả phụ thuộc kinh nghiệm cá nhân",
            "thiếu tiêu chí rõ trước khi chuyển công đoạn",
        ),
        technical_mechanism=(
            "Sự cố cần được đọc theo chuỗi triệu chứng, điều kiện vận hành, thông số kiểm soát "
            "và bằng chứng nghiệm thu thay vì xử lý theo cảm tính."
        ),
        likely_causes=(
            "quy trình kiểm soát chưa đủ rõ",
            "thiếu bằng chứng kiểm tra trước khi quyết định",
            "trách nhiệm giữa các công đoạn chưa được chuẩn hóa",
            "điều kiện làm việc thay đổi nhưng chưa được cập nhật vào checklist",
        ),
        inspection_steps=inspections,
        corrective_actions=actions,
        preventive_actions=(
            "chuẩn hóa tiêu chí kiểm tra trước khi bàn giao",
            "ghi ảnh hiện trường và thông số đo cho từng lần xử lý",
            "đào tạo lại điểm bất thường để tổ sản xuất nhận diện sớm",
        ),
        safety_risks=("rủi ro thao tác lại khi chưa cô lập năng lượng hoặc khu vực làm việc",),
        quality_risks=("nguy cơ lỗi lặp lại nếu thiếu bằng chứng nghiệm thu",),
        production_impact="Làm tăng thời gian chờ, thời gian sửa lại và rủi ro trễ bàn giao.",
        checklist_items=inspections,
        hashtags=("#LucidAIStudio", "#KyThuatSanXuat", "#Qaqc"),
        failure_mechanisms=("Sai lệch nhỏ tích lũy thành lỗi hệ thống khi không có điểm dừng kiểm tra và tiêu chí pass/fail rõ.",),
        measurements=("ghi kích thước, thông số vận hành hoặc ảnh lỗi trước/sau sửa",),
        engineering_calculations=("so sánh giá trị đo với giới hạn bản vẽ, WPS, ITP hoặc hướng dẫn OEM đang áp dụng",),
        verification_steps=("kiểm tra lại bằng cùng phương pháp đã phát hiện lỗi", "lưu bằng chứng nghiệm thu trước khi release"),
        engineering_notes=("Không release bằng cảm giác; phải có bằng chứng đo kiểm hoặc ảnh hiện trường.",),
        common_mistakes=("sửa phần nhìn thấy nhưng không khóa điều kiện tạo lỗi", "bỏ qua người chịu trách nhiệm xác nhận sau sửa"),
        lessons_learned=("Biến mỗi lỗi thành một điểm kiểm soát mới trong checklist ca sau.",),
        standards=("ITP nội bộ", "tiêu chí bản vẽ/quy trình hiện hành"),
    )


def _context_playbook(reasoning: ReasoningObject) -> DomainPlaybook | None:
    intelligence = reasoning.topic_context.failure_intelligence
    if not intelligence:
        return None

    base = next(
        (
            playbook
            for playbook in (*DATA_PLAYBOOKS, *PLAYBOOKS)
            if playbook.key == reasoning.topic_context.playbook_key
        ),
        None,
    )
    process = reasoning.topic_context.failure_mode or reasoning.topic
    equipment = ", ".join(
        value
        for value in (
            *reasoning.topic_context.equipment,
            *reasoning.topic_context.components,
        )
        if value
    ) or "thiết bị/khu vực liên quan"
    standards = intelligence.get("standards", ())
    mechanisms = intelligence.get("failure_mechanism", ())
    measurements = intelligence.get("measurements", ())
    calculations = intelligence.get("engineering_calculation", ())
    verification = intelligence.get("verification_steps", ())
    notes = intelligence.get("engineering_notes", ())
    mistakes = intelligence.get("common_mistakes", ())
    lessons = intelligence.get("lessons_learned", ())
    mechanism = (
        (base.technical_mechanism if base is not None else f"{process} cần được xử lý theo dữ liệu hiện trường")
        + (f", tiêu chuẩn {inline(standards, '')}" if standards else "")
        + ": nhận diện triệu chứng, khóa nguyên nhân, sửa đúng tiêu chí và chỉ bàn giao khi có bằng chứng xác nhận."
    )
    return DomainPlaybook(
        key=reasoning.topic_context.playbook_key or process,
        aliases=(reasoning.topic,),
        domain=(base.domain if base is not None else reasoning.topic_context.domain) or "Kỹ thuật hiện trường",
        process=base.process if base is not None else process,
        equipment=base.equipment if base is not None else equipment,
        typical_symptoms=tuple(dict.fromkeys((*(base.typical_symptoms if base is not None else ()), *intelligence.get("symptoms", ())))),
        technical_mechanism=mechanism,
        likely_causes=tuple(dict.fromkeys((*(base.likely_causes if base is not None else ()), *intelligence.get("root_causes", ())))),
        inspection_steps=tuple(dict.fromkeys((*(base.inspection_steps if base is not None else ()), *intelligence.get("inspection_points", ())))),
        corrective_actions=tuple(
            dict.fromkeys(
                (
                    *(base.corrective_actions if base is not None else ()),
                    *intelligence.get("repair_steps", ()),
                    *intelligence.get("verification_steps", ()),
                )
            )
        ),
        preventive_actions=tuple(dict.fromkeys((*(base.preventive_actions if base is not None else ()), *intelligence.get("preventive_actions", ())))),
        safety_risks=tuple(dict.fromkeys((*(base.safety_risks if base is not None else ()), *intelligence.get("safety_notes", ())))),
        quality_risks=base.quality_risks if base is not None else ("nguy cơ lỗi lặp lại nếu thiếu bằng chứng nghiệm thu trước vận hành",),
        production_impact=base.production_impact if base is not None else "Thiết bị hoặc công đoạn liên quan phải giữ trạng thái kiểm soát đến khi sửa chữa và xác nhận đạt.",
        checklist_items=tuple(
            dict.fromkeys(
                (
                    *(base.checklist_items if base is not None else ()),
                    *intelligence.get("inspection_points", ()),
                    *intelligence.get("repair_steps", ()),
                    *intelligence.get("verification_steps", ()),
                    *intelligence.get("safety_notes", ()),
                )
            )
        ),
        hashtags=base.hashtags if base is not None else ("#LucidAIStudio", "#FailureIntelligence", "#BaoTri"),
        match_groups=base.match_groups if base is not None else (),
        extra_corrective_actions=base.extra_corrective_actions if base is not None else (),
        video_subject=base.video_subject if base is not None else "",
        failure_mechanisms=tuple(dict.fromkeys((*(base.failure_mechanisms if base is not None else ()), *mechanisms))),
        measurements=tuple(dict.fromkeys((*(base.measurements if base is not None else ()), *measurements))),
        engineering_calculations=tuple(dict.fromkeys((*(base.engineering_calculations if base is not None else ()), *calculations))),
        verification_steps=tuple(dict.fromkeys((*(base.verification_steps if base is not None else ()), *verification))),
        engineering_notes=tuple(dict.fromkeys((*(base.engineering_notes if base is not None else ()), *notes))),
        common_mistakes=tuple(dict.fromkeys((*(base.common_mistakes if base is not None else ()), *mistakes))),
        lessons_learned=tuple(dict.fromkeys((*(base.lessons_learned if base is not None else ()), *lessons))),
        standards=tuple(dict.fromkeys((*(base.standards if base is not None else ()), *standards))),
    )


PLAYBOOKS: tuple[DomainPlaybook, ...] = (
    DomainPlaybook(
        key="SAW_POROSITY",
        aliases=("saw porosity", "duong han saw ro khi", "han saw bi ro khi", "ro khi moi han saw", "submerged arc porosity", "thuoc han am"),
        domain="Hàn kết cấu thép",
        process="Hàn hồ quang chìm SAW",
        equipment="máy hàn SAW, dây hàn, thuốc hàn và liên kết thép",
        typical_symptoms=("bề mặt đường hàn có lỗ rỗ", "siêu âm phát hiện chỉ thị dạng khí", "mối hàn phải mài sửa hoặc hàn lại", "kết quả VT/UT không đạt"),
        technical_mechanism=(
            "Rỗ khí trong SAW thường hình thành khi hơi ẩm, dầu, rỉ sét hoặc khí bị giữ lại trong vũng hàn. "
            "Nếu dòng hàn, điện áp, tốc độ chạy, stickout hoặc chiều sâu lớp thuốc không ổn định, khí không thoát kịp trước khi kim loại đông đặc."
        ),
        likely_causes=("thuốc hàn ẩm hoặc sấy chưa đủ", "bề mặt thép còn dầu, rỉ, nước hoặc lớp cán", "dây hàn bẩn hoặc bảo quản kém", "dòng hàn, điện áp hoặc tốc độ chạy lệch WPS", "chiều sâu lớp thuốc không đủ che phủ hồ quang"),
        inspection_steps=("kiểm tra hồ sơ sấy và bảo quản thuốc hàn", "kiểm tra dây hàn, đường kính và tình trạng bề mặt", "làm sạch mép hàn rồi xác nhận không còn dầu, rỉ hoặc ẩm", "đối chiếu dòng hàn, điện áp, tốc độ chạy và stickout với WPS", "kiểm tra chiều sâu lớp thuốc", "thực hiện VT và UT theo ITP"),
        corrective_actions=("mài bỏ vùng rỗ khí đến kim loại tốt", "làm sạch mép hàn và vùng lân cận", "sấy hoặc thay thuốc hàn nghi ngờ ẩm", "đặt lại dòng hàn, điện áp, tốc độ chạy và stickout theo WPS", "hàn sửa theo WPS rồi kiểm tra lại VT/UT"),
        preventive_actions=("quản lý lò sấy và thùng giữ nhiệt thuốc hàn bằng nhật ký", "che chắn thuốc hàn khỏi ẩm và tạp chất", "khóa dải thông số SAW theo WPS tại máy", "kiểm tra bề mặt trước khi rải thuốc", "duy trì điểm dừng kiểm tra VT/UT trước khi chuyển công đoạn"),
        safety_risks=("bỏng, khói hàn và tia hồ quang khi mài sửa hoặc hàn lại", "nguy cơ kẹt tay khi thao tác dầm thép nặng"),
        quality_risks=("mối hàn bị loại, giảm độ kín và giảm độ tin cậy kết cấu", "phát sinh sửa chữa nhiều lần nếu không khóa nguyên nhân ẩm bẩn"),
        production_impact="Gây dừng kiểm tra, tăng giờ mài sửa, tốn thuốc hàn/dây hàn và chậm bàn giao sang công đoạn sơn hoặc lắp dựng.",
        checklist_items=("sấy thuốc hàn", "kiểm tra dây hàn", "làm sạch mép hàn", "kiểm tra dầu/rỉ/ẩm", "kiểm tra dòng hàn, điện áp và tốc độ chạy", "kiểm tra chiều sâu lớp thuốc", "kiểm tra stickout", "VT/UT", "sửa chữa theo WPS"),
        hashtags=("#SAW", "#RoKhiMoiHan", "#WPS", "#VTUT", "#KetCauThep"),
        match_groups=(("saw", "ro khi"), ("saw", "porosity"), ("saw", "bo khi")),
        extra_corrective_actions=("- sấy thuốc hàn và sửa hàn theo WPS đã phê duyệt",),
        video_subject="SAW, thuốc hàn, đường hàn rỗ khí, WPS, VT/UT và thợ hàn mặc bảo hộ",
    ),
    DomainPlaybook(
        key="POWER_TOOL_BREAKDOWN",
        aliases=("may mai cam tay hong lien tuc", "angle grinder breakdown", "may mai hong", "power tool breakdown", "dung cu dien hong lien tuc"),
        domain="Bảo trì dụng cụ điện cầm tay",
        process="Mài sửa và bảo trì dụng cụ",
        equipment="máy mài cầm tay, chổi than, bạc đạn, rotor/stator, công tắc và dây nguồn",
        typical_symptoms=("máy mài nóng nhanh", "tia lửa ở cổ góp nhiều", "rung hoặc ồn bất thường", "máy yếu lực hoặc dừng đột ngột", "hỏng lặp lại sau thời gian ngắn"),
        technical_mechanism=(
            "Máy mài hỏng liên tục thường đến từ mòn chổi than, bạc đạn rơ, bụi mài lọt vào thân máy, rotor/stator quá nhiệt hoặc công tắc và dây nguồn tiếp xúc kém. "
            "Khi công nhân ép tải, dùng sai đá hoặc không vệ sinh khe gió, nhiệt và bụi làm hỏng cách điện nhanh hơn."
        ),
        likely_causes=("chổi than mòn hoặc kẹt trong rãnh giữ", "bạc đạn khô mỡ, rơ hoặc kêu", "bụi mài bám trong khe gió và cổ góp", "rotor/stator quá nhiệt do quá tải", "dây nguồn hoặc công tắc chập chờn", "công nhân ép máy hoặc dùng sai đá mài"),
        inspection_steps=("mở kiểm tra chổi than và cổ góp", "quay thử bạc đạn để nghe ồn và cảm nhận độ rơ", "thổi sạch bụi mài trong khe gió", "kiểm tra rotor/stator bằng quan sát cháy xém và đo cách điện khi cần", "kiểm tra công tắc, dây nguồn và phích cắm", "quan sát cách công nhân sử dụng máy tại hiện trường"),
        corrective_actions=("thay chổi than đúng mã", "thay bạc đạn khi có rơ, ồn hoặc nóng", "vệ sinh bụi mài và khe thông gió", "loại bỏ rotor/stator cháy hoặc suy cách điện", "thay công tắc hoặc dây nguồn lỗi", "hướng dẫn lại cách ép lực và chọn đá mài"),
        preventive_actions=("lập lịch bảo trì định kỳ theo giờ sử dụng", "kiểm tra rung/ồn/nhiệt trước ca", "quy định vệ sinh bụi mài cuối ca", "cấp đá mài đúng công việc", "kiểm soát cách sử dụng của công nhân bằng hướng dẫn ngắn tại xưởng"),
        safety_risks=("điện giật do dây nguồn hoặc công tắc hỏng", "vỡ đá mài khi quá tải hoặc dùng sai tốc độ", "bụi và tia lửa gây thương tích nếu thiếu PPE"),
        quality_risks=("bề mặt mài không đều, mất kích thước hoặc làm hỏng mép hàn cần sửa",),
        production_impact="Làm gián đoạn mài sửa, tăng thời gian chờ dụng cụ, tăng chi phí thay máy và tạo áp lực tiến độ cho tổ hoàn thiện.",
        checklist_items=("chổi than", "bạc đạn", "rotor/stator", "công tắc", "dây nguồn", "bụi mài", "quá tải", "rung/ồn/nhiệt", "lịch bảo trì", "hướng dẫn vận hành"),
        hashtags=("#MayMai", "#BaoTri", "#DungCuDien", "#TPM", "#AnToanLaoDong"),
        match_groups=(("may mai", "hong"), ("angle grinder", "breakdown"), ("may mai", "lien tuc")),
        extra_corrective_actions=("- kiểm tra công tắc/dây nguồn, ghi rung/ồn/nhiệt và huấn luyện công nhân dùng máy mài cầm tay đúng tải",),
        video_subject="máy mài cầm tay, chổi than, bạc đạn, bụi mài, công tắc, dây nguồn và bảo hộ",
    ),
    DomainPlaybook(
        key="LASER_5S",
        aliases=("5s khu vuc may cat laser", "laser 5s", "5s laser cutting", "may cat laser 5s"),
        domain="Lean/5S khu vực cắt",
        process="5S cho máy cắt laser",
        equipment="máy cắt laser, bàn cắt, khu vật tư đầu vào, khu thành phẩm và thùng phế",
        typical_symptoms=("vật tư lẫn lộn", "phôi sau cắt khó truy vết", "dụng cụ và đầu cắt không có vị trí cố định", "phế và bavia tích tụ quanh bàn cắt"),
        technical_mechanism="5S yếu làm dòng vật tư không rõ, tăng nguy cơ lẫn chi tiết, mất thời gian tìm dụng cụ và che khuất bất thường của máy cắt laser.",
        likely_causes=("chưa phân làn vật tư đầu vào và đầu ra", "không có tiêu chuẩn ảnh sau ca", "thiếu chủ khu vực", "dụng cụ đo và phụ kiện laser chưa có bảng vị trí cố định"),
        inspection_steps=("đối chiếu ảnh chuẩn 5S", "kiểm tra nhãn bán thành phẩm và mã chi tiết", "kiểm tra thùng phế, bavia và đường đi", "kiểm tra vị trí đầu cắt, thấu kính, thước đo và dụng cụ vệ sinh"),
        corrective_actions=("vạch lại luồng vật tư", "dán nhãn khu phôi, thành phẩm và phế", "lập bảng vị trí dụng cụ", "dọn bavia và phế sau từng ca"),
        preventive_actions=("chụp ảnh chuẩn cuối ca", "gán chủ khu vực", "kiểm tra 5S hằng ngày", "đưa điểm 5S vào họp sản xuất"),
        safety_risks=("trượt ngã do phế và bavia", "đứt tay khi phân loại chi tiết sắc cạnh"),
        quality_risks=("lẫn mã chi tiết, xước bề mặt, giao nhầm bán thành phẩm",),
        production_impact="Giảm tốc độ cấp phôi, tăng thời gian tìm kiếm và làm chậm công đoạn gá lắp sau cắt.",
        checklist_items=("phân làn vật tư", "nhãn bán thành phẩm", "thùng phế", "bảng vị trí dụng cụ", "ảnh chuẩn 5S", "chủ khu vực", "vệ sinh bàn cắt", "kiểm tra đầu cắt/thấu kính"),
        hashtags=("#5S", "#CatLaser", "#SanXuatTinhGon", "#Kaizen"),
        match_groups=(("laser", "5s"),),
    ),
    DomainPlaybook(
        key="PAINT_PEELING",
        aliases=("loi bong troc son", "paint peeling", "coating peeling", "son bong troc", "do bam dinh son kem"),
        domain="Sơn phủ kết cấu thép",
        process="Chuẩn bị bề mặt và sơn phủ",
        equipment="bề mặt thép, hệ sơn, thiết bị phun và dụng cụ đo môi trường",
        typical_symptoms=("màng sơn bong theo mảng", "lộ nền thép sau va chạm nhẹ", "kết quả adhesion không đạt", "xuất hiện rỉ dưới lớp sơn"),
        technical_mechanism="Sơn bong tróc xảy ra khi bề mặt còn dầu, muối, bụi, ẩm hoặc độ nhám không đạt làm liên kết giữa màng sơn và nền thép suy yếu.",
        likely_causes=("profile phun bi không đạt", "sơn khi gần điểm sương", "bề mặt còn dầu hoặc bụi", "thời gian phủ lớp kế tiếp sai", "pha sơn hoặc đóng rắn không đúng"),
        inspection_steps=("kiểm tra độ sạch bề mặt", "đo độ nhám", "ghi nhiệt độ thép, độ ẩm và điểm sương", "kiểm tra DFT", "thử bám dính bằng phương pháp cắt ô hoặc kéo bật khi cần"),
        corrective_actions=("loại bỏ vùng sơn lỗi", "làm sạch và tạo nhám lại", "sơn lại theo quy trình", "đo DFT và kiểm tra bám dính sau sửa"),
        preventive_actions=("khóa điều kiện môi trường trước khi sơn", "kiểm soát vật tư pha trộn", "ghi profile và DFT theo khu vực", "bảo vệ bề mặt sau phun bi"),
        safety_risks=("hít dung môi và bụi sơn", "cháy nổ nếu thông gió kém"),
        quality_risks=("ăn mòn sớm, khách hàng từ chối nghiệm thu, phải sơn lại diện rộng",),
        production_impact="Tăng thời gian reblast, repaint, kiểm tra lại và chiếm mặt bằng hoàn thiện.",
        checklist_items=("độ sạch bề mặt", "độ nhám", "điểm sương", "độ ẩm", "DFT", "độ bám dính", "cắt ô/kéo bật", "vát mép vùng sửa"),
        hashtags=("#SonPhu", "#DoBamDinh", "#DFT", "#ChuanBiBeMat"),
        match_groups=(("son", "bong troc"), ("paint", "peeling"), ("coating", "adhesion")),
    ),
    DomainPlaybook(
        key="MOTOR_VIBRATION",
        aliases=("motor vibration", "dong co bi rung", "do rung dong co", "motor rung", "may rung"),
        domain="Bảo trì thiết bị quay",
        process="Chẩn đoán rung động động cơ",
        equipment="động cơ, bạc đạn, khớp nối, bệ máy và tải kéo",
        typical_symptoms=("động cơ rung tăng", "bạc đạn nóng", "tiếng ồn theo chu kỳ", "dòng điện dao động"),
        technical_mechanism="Rung động tăng khi mất cân bằng, lệch tâm, bạc đạn hỏng hoặc bệ máy lỏng truyền lực dao động vào thân động cơ.",
        likely_causes=("lệch tâm khớp nối", "bạc đạn mòn", "rotor mất cân bằng", "bu lông bệ lỏng", "tải bị kẹt hoặc quá tải"),
        inspection_steps=("đo rung theo trục H/V/A", "đo nhiệt bạc đạn", "kiểm tra căn chỉnh bằng laser", "kiểm tra bu lông bệ", "đo dòng điện"),
        corrective_actions=("căn chỉnh khớp nối", "thay bạc đạn lỗi", "cân bằng rotor", "siết và chêm lại bệ", "xử lý tải quá tải"),
        preventive_actions=("theo dõi xu hướng rung", "bôi trơn đúng lịch", "kiểm tra đồng tâm sau sửa chữa", "lập ngưỡng cảnh báo"),
        safety_risks=("vỡ khớp nối hoặc bung chi tiết quay",),
        quality_risks=("dừng máy làm gián đoạn công đoạn phụ thuộc",),
        production_impact="Có thể gây dừng máy đột xuất và kéo dài thời gian sửa cơ điện.",
        checklist_items=("đo rung", "nhiệt bạc đạn", "kiểm tra đồng tâm", "bôi trơn", "bu lông bệ", "dòng điện", "xu hướng dữ liệu"),
        hashtags=("#DongCo", "#DoRung", "#BaoTri", "#TPM"),
    ),
    DomainPlaybook(
        key="ANCHOR_BOLT_MISLOCATION",
        aliases=("anchor bolt mislocation", "bu long neo sai vi tri", "bulong neo sai vi tri", "anchor sai vi tri"),
        domain="Lắp dựng kết cấu thép",
        process="Kiểm soát bu lông neo",
        equipment="bu lông neo, template, base plate và móng",
        typical_symptoms=("lỗ base plate không khớp", "khoảng cách tim bu lông lệch", "cao độ ren không đủ", "cột không thể dựng đúng vị trí"),
        technical_mechanism="Sai vị trí bu lông neo thường phát sinh khi template yếu, mốc khảo sát sai hoặc không kiểm tra lại trước khi đổ bê tông.",
        likely_causes=("template không cứng", "mốc survey sai", "bu lông xê dịch khi đổ bê tông", "không nghiệm thu trước đổ"),
        inspection_steps=("survey tọa độ tim bu lông", "kiểm tra cao độ projection", "kiểm tra ren và độ thẳng", "đối chiếu bản vẽ mới nhất"),
        corrective_actions=("lập phương án sửa được phê duyệt", "khoan/cấy hoặc mở lỗ theo thiết kế cho phép", "bảo vệ ren và kiểm tra lại survey"),
        preventive_actions=("dùng template cứng", "hold point trước đổ bê tông", "khóa revision bản vẽ", "lưu biên bản survey"),
        safety_risks=("rủi ro khi nâng cột mà điểm kê không ổn định",),
        quality_risks=("lệch trục cột, sai dung sai lắp dựng, phát sinh NCR",),
        production_impact="Làm chậm lắp dựng, tăng chi phí sửa móng/base plate và ảnh hưởng tiến độ cẩu.",
        checklist_items=("tọa độ tim", "projection", "template", "ren", "bản vẽ revision", "biên bản survey", "hold point"),
        hashtags=("#BuLongNeo", "#LapDung", "#KhaoSat", "#KetCauThep"),
    ),
    DomainPlaybook(
        key="BLASTING_ABRASIVE_LOSS",
        aliases=("blasting abrasive loss", "hao hat bi phun", "mat hat phun bi", "abrasive loss", "phun bi ton hat"),
        domain="Xử lý bề mặt",
        process="Phun bi/phun cát",
        equipment="buồng phun, hạt mài, hệ thu hồi, cyclone và lọc bụi",
        typical_symptoms=("hao hạt mài bất thường", "bụi tăng", "profile không ổn định", "năng suất phun giảm"),
        technical_mechanism="Hạt mài thất thoát khi hệ thu hồi kín kém, phân ly bụi sai, áp lực phun không phù hợp hoặc thao tác phun làm hạt văng khỏi vùng thu hồi.",
        likely_causes=("rò rỉ cửa buồng phun", "cyclone phân ly kém", "áp lực phun quá cao", "hạt bị vỡ do tái sử dụng quá lâu", "thu gom sàn không đều"),
        inspection_steps=("kiểm tra rò rỉ buồng phun", "kiểm tra hệ thu hồi", "đo độ nhám", "kiểm tra bụi và kích cỡ hạt", "ghi lượng hạt bổ sung mỗi ca"),
        corrective_actions=("bịt kín điểm rò", "chỉnh bộ phân ly", "đặt lại áp lực phun", "loại hạt vỡ và bụi", "chuẩn hóa thu gom"),
        preventive_actions=("theo dõi tiêu hao hạt theo m2", "bảo trì gioăng cửa", "kiểm tra lọc bụi định kỳ", "đào tạo góc phun"),
        safety_risks=("bụi hô hấp và trơn trượt do hạt rơi vãi",),
        quality_risks=("độ nhám không đạt làm giảm bám dính sơn",),
        production_impact="Tăng chi phí vật tư, giảm tốc độ chuẩn bị bề mặt và ảnh hưởng kế hoạch sơn.",
        checklist_items=("rò buồng phun", "hệ thu hồi", "bộ phân ly", "áp lực phun", "độ nhám", "lượng hạt bổ sung", "lọc bụi"),
        hashtags=("#PhunBi", "#HatMai", "#ChuanBiBeMat", "#KiemSoatChiPhi"),
    ),
    DomainPlaybook(
        key="LASER_BURR",
        aliases=("laser burr", "laser dross", "ba via cat laser", "bavia laser", "xi cat laser"),
        domain="Cắt laser",
        process="Kiểm soát bavia/xỉ cắt",
        equipment="máy cắt laser, đầu cắt, thấu kính, khí hỗ trợ và bàn cắt",
        typical_symptoms=("mép cắt có bavia", "xỉ bám mặt dưới", "lỗ cắt không sạch", "phôi phải mài lại nhiều"),
        technical_mechanism="Bavia laser xuất hiện khi tiêu điểm, tốc độ cắt, công suất, áp lực khí hoặc tình trạng đầu cắt/thấu kính không phù hợp với chiều dày vật liệu.",
        likely_causes=("tiêu điểm sai", "đầu cắt mòn hoặc lệch tâm", "áp lực khí hỗ trợ thấp", "tốc độ cắt không phù hợp", "thấu kính bẩn"),
        inspection_steps=("kiểm tra đầu cắt và thấu kính", "cắt mẫu theo chiều dày", "đối chiếu tiêu điểm, công suất, tốc độ và khí", "kiểm tra mép dưới bằng mẫu chuẩn"),
        corrective_actions=("vệ sinh hoặc thay thấu kính/đầu cắt", "đặt lại tiêu điểm", "tối ưu tốc độ và khí", "mài sạch bavia trước gá lắp"),
        preventive_actions=("lập bảng thông số theo chiều dày", "kiểm tra đầu cắt/thấu kính đầu ca", "lưu mẫu cắt chuẩn", "tách phôi lỗi để xử lý ngay"),
        safety_risks=("đứt tay do mép sắc",),
        quality_risks=("fit-up hở, mối hàn xấu hoặc lắp ghép kẹt do bavia",),
        production_impact="Tăng thời gian mài sửa và làm chậm công đoạn gá lắp.",
        checklist_items=("đầu cắt", "thấu kính", "tiêu điểm", "khí hỗ trợ", "tốc độ cắt", "mẫu cắt", "bavia mép dưới"),
        hashtags=("#CatLaser", "#Bavia", "#XiCat", "#Fitup"),
    ),
    DomainPlaybook(
        key="CRANE_NOISE",
        aliases=("crane noise", "cau truc keu", "cau truc on", "tieng on cau truc", "overhead crane noise"),
        domain="Bảo trì thiết bị nâng",
        process="Chẩn đoán tiếng ồn cầu trục",
        equipment="cầu trục, bánh xe, ray, hộp giảm tốc, phanh và cáp tải",
        typical_symptoms=("cầu trục kêu khi di chuyển", "rung trên dầm", "bánh xe mòn lệch", "phanh phát tiếng bất thường"),
        technical_mechanism="Tiếng ồn cầu trục thường đến từ lệch ray, bánh xe mòn, bạc đạn thiếu bôi trơn, hộp giảm tốc lỗi hoặc phanh cọ sát.",
        likely_causes=("ray lệch hoặc bẩn", "bánh xe mòn côn", "bạc đạn khô", "hộp giảm tốc thiếu dầu", "phanh chỉnh sai"),
        inspection_steps=("kiểm tra ray và khe hở", "kiểm tra bánh xe", "nghe hộp giảm tốc", "kiểm tra dầu và bạc đạn", "thử phanh không tải và có tải"),
        corrective_actions=("vệ sinh và căn ray", "thay bánh xe hoặc bạc đạn lỗi", "bổ sung dầu hộp giảm tốc", "chỉnh phanh theo hướng dẫn"),
        preventive_actions=("lập lịch kiểm tra ray", "bôi trơn định kỳ", "ghi âm/rung để so sánh", "không vận hành quá tải"),
        safety_risks=("rủi ro rơi tải hoặc mất kiểm soát di chuyển nếu tiếp tục vận hành",),
        quality_risks=("dừng nâng hạ làm chậm xuất hàng và lắp dựng",),
        production_impact="Có thể khóa thiết bị nâng chính, gây ùn vật tư và chậm giao hàng.",
        checklist_items=("ray", "bánh xe", "bạc đạn", "hộp giảm tốc", "phanh", "cáp tải", "dầu bôi trơn", "thử tải"),
        hashtags=("#CauTruc", "#BaoTri", "#AnToanNangHa", "#TPM"),
    ),
    DomainPlaybook(
        key="DFT_LOW",
        aliases=("dft low", "dft thap", "do day mang son thap", "son khong dat dft", "low dry film thickness"),
        domain="Sơn phủ kết cấu thép",
        process="Kiểm soát DFT",
        equipment="màng sơn khô, máy đo DFT, súng phun và bề mặt thép",
        typical_symptoms=("DFT thấp hơn yêu cầu", "spot reading không đạt", "màng sơn phủ không đều", "phải sơn bù nhiều điểm"),
        technical_mechanism="DFT thấp xảy ra khi lượng sơn ướt, khoảng cách phun, tốc độ tay, độ phủ mép cạnh hoặc pha loãng không kiểm soát đúng theo quy trình.",
        likely_causes=("tay phun đi quá nhanh", "pha loãng quá mức", "không stripe coat mép cạnh", "máy đo chưa hiệu chuẩn", "bề mặt khó phủ đều"),
        inspection_steps=("hiệu chuẩn máy đo DFT", "lập bản đồ điểm đo", "kiểm tra WFT khi phun", "kiểm tra mép cạnh và góc khuất", "đối chiếu yêu cầu hệ sơn"),
        corrective_actions=("sơn bù vùng thấp DFT", "kiểm tra lại sau khô", "điều chỉnh kỹ thuật phun", "ghi lại map DFT sau sửa"),
        preventive_actions=("đào tạo tay phun", "sơn dặm mép cạnh trước lớp phủ chính", "kiểm soát WFT trong ca", "hiệu chuẩn máy đo trước khi dùng"),
        safety_risks=("phơi nhiễm dung môi khi sơn bù nhiều lần",),
        quality_risks=("chống ăn mòn không đạt tuổi thọ thiết kế", "khách hàng từ chối nghiệm thu"),
        production_impact="Làm tăng thời gian sơn bù, chờ khô và kiểm tra lại.",
        checklist_items=("hiệu chuẩn máy đo DFT", "bản đồ điểm đo", "WFT", "sơn dặm mép cạnh", "mép cạnh", "pha loãng", "sơn bù", "kiểm tra sau khô"),
        hashtags=("#DFT", "#SonPhu", "#KiemTraSon", "#Qaqc"),
    ),
)


def _domain_playbook_from_engineering(playbook: EngineeringPlaybook) -> DomainPlaybook:
    checklist_items = (
        *playbook.inspection_procedure,
        *playbook.measurements,
        *playbook.acceptance_criteria,
        *playbook.verification_after_repair,
    )
    return DomainPlaybook(
        key=playbook.key,
        aliases=playbook.aliases,
        domain=playbook.domain,
        process=playbook.process,
        equipment=", ".join(playbook.equipment),
        typical_symptoms=playbook.symptoms,
        technical_mechanism=" ".join(playbook.failure_mechanism),
        likely_causes=tuple(root_cause.cause for root_cause in playbook.root_causes),
        inspection_steps=playbook.inspection_procedure,
        corrective_actions=playbook.repair_procedure_sop,
        preventive_actions=playbook.preventive_maintenance,
        safety_risks=playbook.safety_risks,
        quality_risks=playbook.quality_risks,
        production_impact=playbook.production_impact,
        checklist_items=tuple(dict.fromkeys(checklist_items)),
        hashtags=playbook.hashtags,
        match_groups=playbook.match_groups,
        failure_mechanisms=playbook.failure_mechanism,
        measurements=playbook.measurements,
        engineering_calculations=playbook.acceptance_criteria,
        verification_steps=playbook.verification_after_repair,
        engineering_notes=playbook.lessons_learned,
        common_mistakes=playbook.common_mistakes,
        lessons_learned=playbook.lessons_learned,
        standards=playbook.related_standards,
    )


def _profile_data_playbooks() -> tuple[DomainPlaybook, ...]:
    path = Path(__file__).resolve().parents[1] / "topic_intelligence_profiles.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    playbooks = []
    for item in raw.get("playbooks", ()):
        if not item.get("typical_symptoms"):
            continue
        playbooks.append(
            DomainPlaybook(
                key=item["key"],
                aliases=tuple(item.get("aliases", ())),
                domain=item["domain"],
                process=item["process"],
                equipment=item["equipment"],
                typical_symptoms=tuple(item.get("typical_symptoms", ())),
                technical_mechanism=item.get("technical_mechanism", ""),
                likely_causes=tuple(item.get("likely_causes", ())),
                inspection_steps=tuple(item.get("inspection_steps", ())),
                corrective_actions=tuple(item.get("corrective_actions", ())),
                preventive_actions=tuple(item.get("preventive_actions", ())),
                safety_risks=tuple(item.get("safety_risks", ())),
                quality_risks=tuple(item.get("quality_risks", ())),
                production_impact=item.get("production_impact", ""),
                checklist_items=tuple(item.get("checklist_items", ())),
                hashtags=tuple(item.get("hashtags", ())),
                match_groups=(),
                extra_corrective_actions=tuple(item.get("extra_corrective_actions", ())),
                video_subject=item.get("video_subject", ""),
                failure_mechanisms=tuple(item.get("failure_mechanisms", ())),
                measurements=tuple(item.get("measurements", ())),
                engineering_calculations=tuple(item.get("engineering_calculations", ())),
                verification_steps=tuple(item.get("verification_steps", ())),
                engineering_notes=tuple(item.get("engineering_notes", ())),
                common_mistakes=tuple(item.get("common_mistakes", ())),
                lessons_learned=tuple(item.get("lessons_learned", ())),
                standards=tuple(item.get("standards", ())),
            )
        )
    return tuple(playbooks)


def _data_playbooks() -> tuple[DomainPlaybook, ...]:
    engineering_playbooks = tuple(
        _domain_playbook_from_engineering(playbook)
        for playbook in EngineeringKnowledgeLibrary().all()
    )
    legacy_profile_playbooks = tuple(
        playbook
        for playbook in _profile_data_playbooks()
        if playbook.key not in {item.key for item in engineering_playbooks}
    )
    return (*engineering_playbooks, *legacy_profile_playbooks)


DATA_PLAYBOOKS = _data_playbooks()


def _fuzzy_confidence(playbook: DomainPlaybook, haystack: str) -> float:
    confidence = 0.0
    for alias in playbook.aliases:
        normalized_alias = _normalize(alias)
        if not normalized_alias:
            continue
        if _contains_term(haystack, normalized_alias):
            confidence = max(confidence, 1.0)
            continue
        tokens = normalized_alias.split()
        if tokens:
            hits = sum(1 for token in tokens if _contains_term(haystack, token))
            confidence = max(confidence, hits / len(tokens) * 0.5)
    for group in playbook.match_groups:
        if group and all(_contains_term(haystack, term) for term in group):
            confidence = max(confidence, 1.0)
    return confidence


def match_playbook(topic: str, reasoning: ReasoningObject | None = None) -> DomainPlaybook | None:
    if reasoning is not None:
        context_playbook = _context_playbook(reasoning)
        if context_playbook is not None:
            return context_playbook

    if reasoning is not None and reasoning.topic_context.playbook_key:
        for playbook in (*DATA_PLAYBOOKS, *PLAYBOOKS):
            if playbook.key == reasoning.topic_context.playbook_key:
                return playbook

    values = [topic]
    if reasoning is not None:
        values.extend(reasoning.parsed.keywords)
        for category in ("Process", "Machine", "Tool", "Defect", "Failure", "Measurement", "Component", "Material"):
            values.extend(reasoning.entities.get(category))
    haystack = _normalize(" ".join(values))
    best: tuple[int, DomainPlaybook] | None = None
    for playbook in (*DATA_PLAYBOOKS, *PLAYBOOKS):
        score = 0
        for alias in playbook.aliases:
            normalized_alias = _normalize(alias)
            if normalized_alias and normalized_alias in haystack:
                score += 12 + len(normalized_alias.split())
            else:
                score += sum(1 for token in normalized_alias.split() if token in haystack)
        score += 20 * sum(
            1
            for group in playbook.match_groups
            if all(_contains_term(haystack, term) for term in group)
        )
        if best is None or score > best[0]:
            best = (score, playbook)
    if best is None or best[0] <= 0:
        return _fallback_playbook(reasoning) if reasoning is not None else None
    if reasoning is not None and not reasoning.topic_context.playbook_key:
        if _fuzzy_confidence(best[1], haystack) < 0.9:
            return _fallback_playbook(reasoning)
    return best[1]


def playbook_for_reasoning(reasoning: ReasoningObject) -> DomainPlaybook:
    return match_playbook(reasoning.topic, reasoning) or _fallback_playbook(reasoning)


def _contains_term(haystack: str, term: str) -> bool:
    normalized_term = _normalize(term)
    if not normalized_term:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
    return re.search(pattern, haystack) is not None


def bullets(values: tuple[str, ...], limit: int = 4) -> list[str]:
    return [f"- {value}" for value in values[:limit]]


def inline(values: tuple[str, ...], fallback: str) -> str:
    return ", ".join(values) if values else fallback


def pick(reasoning: ReasoningObject, values: tuple[str, ...], salt: str = "") -> str:
    if not values:
        return ""
    seed = hashlib.sha256(f"{reasoning.topic}:{salt}".encode("utf-8")).hexdigest()
    return values[int(seed[:8], 16) % len(values)]


def subject(reasoning: ReasoningObject) -> str:
    return inline(
        (
            *reasoning.entities.get("Process")[:1],
            *reasoning.entities.get("Machine")[:1],
            *reasoning.entities.get("Defect")[:1],
            *reasoning.entities.get("Failure")[:1],
        ),
        reasoning.topic,
    )


def facts(reasoning: ReasoningObject) -> list[str]:
    return [f"- {fact.text}" for fact in reasoning.knowledge_facts[:3]]


def hashtags(reasoning: ReasoningObject) -> str:
    tags = ["#MaithuyELEC", "#LucidAIStudio", "#BaoTriCongNghiep"]
    playbook = playbook_for_reasoning(reasoning)
    for tag in playbook.hashtags:
        if tag not in tags:
            tags.append(tag)
    for value in (
        *reasoning.entities.get("Process"),
        *reasoning.entities.get("Defect"),
        *reasoning.entities.get("Machine"),
        *reasoning.entities.get("Equipment"),
        *reasoning.entities.get("Component"),
    ):
        tag = "#" + "".join(part.capitalize() for part in value.replace("/", " ").split())
        if tag not in tags:
            tags.append(tag)
    return " ".join(tags[:10])


def sanitize_user_output(text: str) -> str:
    replacements = {
        "TopicContext": "",
        "Playbook": "",
        "ReasoningObject": "",
        "Problem Description": "Mô tả sự cố",
        "Engineering Principle": "Nguyên lý kỹ thuật",
        "Failure Mechanism": "Cơ chế hư hỏng",
        "Failure Modes": "Dạng hư hỏng",
        "Root Cause": "Nguyên nhân gốc",
        "Cause Type": "Nhóm nguyên nhân",
        "Symptoms": "Dấu hiệu nhận biết",
        "Inspection": "Phương pháp kiểm tra",
        "Measurement": "Đo kiểm",
        "Tools": "Dụng cụ",
        "Decision": "Tiêu chí kết luận",
        "Corrective Action": "Hành động khắc phục",
        "Preventive Action": "Phòng ngừa tái diễn",
        "Risk If Ignored": "Rủi ro nếu bỏ qua",
        "Confidence": "Mức độ tin cậy",
        "release": "bàn giao",
        "Release": "Bàn giao",
        "pass/fail": "đạt/không đạt",
        "material/equipment": "vật tư hoặc thiết bị",
        "có thể": "có nguy cơ",
        "Có thể": "Có nguy cơ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


class ChannelWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call(
            "Channel Writer",
            self,
            selected_topic=reasoning.topic,
            selected_domain=reasoning.topic_context.domain,
            selected_playbook=reasoning.topic_context.playbook_key,
            writer_selected=plan.channel,
            writer_class=self.__class__.__name__,
            knowledge_count=len(reasoning.knowledge_facts),
        )
        if plan.channel == "hashtags":
            return hashtags(reasoning)
        from hgpt_ai_os.topic_engine.writers.engineering_document_writer import EngineeringDocumentWriter

        trace_call(
            "Selected writer",
            self,
            selected_topic=reasoning.topic,
            selected_playbook=reasoning.topic_context.playbook_key,
            writer_selected="EngineeringDocumentWriter",
            writer_class=EngineeringDocumentWriter.__name__,
        )
        return EngineeringDocumentWriter().write(reasoning, plan)


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ChannelWriter)
