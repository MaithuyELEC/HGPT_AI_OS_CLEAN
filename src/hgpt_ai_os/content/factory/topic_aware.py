from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class TopicProfile:
    topic: str
    normalized: str
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]
    hashtags: tuple[str, ...]


BASE_HASHTAGS = (
    "#MaithuyELEC",
    "#LucidAuto",
    "#HGPTSteel",
    "#SteelKnowledgeBase",
    "#DigitalFactory",
)


class TopicClassifier:
    def classify(self, topic: str) -> TopicProfile:
        title = (topic or "").strip() or "Cải tiến xưởng sản xuất kết cấu thép"
        normalized = self._normalize(title)

        if self._has(normalized, "5s", "kaizen", "lean"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="5S / kaizen / lean",
                subject="5S trong xưởng sản xuất kết cấu thép",
                problem="khu vực làm việc khó kiểm soát vì vật tư, máy móc, dụng cụ, phôi thép và bán thành phẩm chưa được sắp xếp theo luồng sản xuất",
                objects=(
                    "vật tư",
                    "máy móc",
                    "dụng cụ",
                    "phôi thép",
                    "bán thành phẩm",
                    "khu vực cắt, hàn, gá lắp và xuất hàng",
                ),
                risks=(
                    "mất an toàn khi di chuyển trong xưởng",
                    "tốn thời gian tìm dụng cụ",
                    "giảm năng suất tổ hàn và tổ lắp",
                    "tăng lãng phí do đặt sai vị trí hoặc làm lại",
                ),
                causes=(
                    "chưa có vị trí chuẩn cho dụng cụ và bán thành phẩm",
                    "thiếu nhãn nhận diện theo khu vực",
                    "không duy trì kiểm tra 5S theo ca",
                ),
                actions=(
                    "phân luồng vật tư, phôi thép và bán thành phẩm theo từng công đoạn",
                    "kẻ vạch, gắn nhãn, lập shadow board cho dụng cụ dùng chung",
                    "kiểm tra 5S đầu ca và cuối ca bằng checklist ngắn",
                    "đo thời gian tìm dụng cụ và số điểm mất an toàn sau mỗi tuần",
                ),
                signs=(
                    "dụng cụ để lẫn trên bàn gá hoặc sàn xưởng",
                    "bán thành phẩm không có thẻ nhận dạng",
                    "lối đi bị chiếm bởi vật tư chờ xử lý",
                ),
                hashtags=("#5S", "#Kaizen", "#LeanManufacturing", "#SteelWorkshop"),
            )

        if self._has(normalized, "han", "welding", "weld", "mig", "saw", "fit up", "fitup", "ro khi", "porosity"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="welding / SAW / MIG / fit-up",
                subject="kiểm soát chất lượng hàn trong kết cấu thép",
                problem=self._welding_problem(normalized),
                objects=(
                    "mép hàn",
                    "khe hở fit-up",
                    "dây hàn",
                    "khí bảo vệ",
                    "thông số dòng áp",
                    "mối hàn hoàn thiện",
                ),
                risks=(
                    "mối hàn không đạt nghiệm thu",
                    "phải mài sửa hoặc hàn lại",
                    "trễ tiến độ bàn giao cấu kiện",
                    "tăng chi phí vật tư hàn và nhân công",
                ),
                causes=(
                    "bề mặt hàn còn ẩm, dầu hoặc gỉ",
                    "lưu lượng khí bảo vệ không ổn định",
                    "thợ hàn đặt tốc độ hoặc góc mỏ chưa phù hợp",
                    "fit-up chưa được kiểm tra trước khi hàn",
                ),
                actions=(
                    "làm sạch mép hàn và xác nhận fit-up trước khi mồi hồ quang",
                    "kiểm tra khí bảo vệ, dây hàn và thông số máy MIG/SAW",
                    "ghi nhận vị trí lỗi bằng ảnh và mã cấu kiện",
                    "chỉ cho sửa khi QA/QC đã xác định nguyên nhân gốc",
                ),
                signs=(
                    "xuất hiện rỗ khí hoặc lỗ nhỏ trên bề mặt mối hàn",
                    "đường hàn không đều màu hoặc có vùng cháy cạnh",
                    "kết quả VT/MT/UT không ổn định giữa các cấu kiện",
                ),
                hashtags=("#Welding", "#MIGWelding", "#QAQC", "#SteelFabrication"),
            )

        if self._has(normalized, "son", "phun bi", "ban bi", "blasting", "painting", "coating", "be mat"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="painting / blasting / coating",
                subject="xử lý bề mặt và sơn phủ kết cấu thép",
                problem="lớp phủ khó đạt độ bám dính và tuổi thọ khi bề mặt thép, độ sạch, độ nhám và điều kiện môi trường chưa được kiểm soát",
                objects=("bề mặt thép", "máy phun bi", "sơn lót", "DFT", "độ nhám", "độ ẩm môi trường"),
                risks=("bong tróc sơn", "ăn mòn sớm", "phải xử lý lại bề mặt", "chậm đóng gói và giao hàng"),
                causes=("bề mặt còn bụi muối hoặc dầu", "độ nhám không đạt", "sơn khi nhiệt độ/độ ẩm không phù hợp"),
                actions=("kiểm tra độ sạch và độ nhám trước sơn", "đo DFT theo điểm chuẩn", "cách ly cấu kiện chưa đạt để sửa đúng quy trình"),
                signs=("màu phủ không đều", "DFT lệch vùng", "bề mặt còn bụi hoặc vết dầu"),
                hashtags=("#Coating", "#Blasting", "#Painting", "#CorrosionControl"),
            )

        if self._has(normalized, "bao tri", "dong co", "motor", "may nen", "compressor", "qua nhiet", "fault"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="maintenance / motor / compressor / machine fault",
                subject="bảo trì thiết bị xưởng kết cấu thép",
                problem=self._maintenance_problem(normalized),
                objects=("động cơ", "máy nén khí", "ổ bi", "quạt làm mát", "lọc gió", "tủ điện", "dòng tải"),
                risks=("dừng máy đột xuất", "giảm áp khí cho dây chuyền", "cháy cuộn dây động cơ", "tăng chi phí sửa chữa và chậm tiến độ"),
                causes=("lọc gió bẩn hoặc thông gió kém", "quá tải kéo dài", "ổ bi thiếu bôi trơn", "điện áp hoặc dòng tải bất thường"),
                actions=("đo nhiệt độ vỏ động cơ và dòng tải theo ca", "vệ sinh lọc gió, kiểm tra quạt và đường thông gió", "lập lịch bảo trì phòng ngừa cho máy nén khí", "dừng máy khi vượt ngưỡng nhiệt cho phép"),
                signs=("vỏ động cơ nóng bất thường", "máy nén khí chạy lâu không nghỉ", "áp suất tụt hoặc tiếng ồn ổ bi tăng"),
                hashtags=("#Maintenance", "#Compressor", "#Motor", "#PreventiveMaintenance"),
            )

        if self._has(normalized, "qaqc", "qc", "inspection", "kiem tra", "ncr", "checklist", "nghiem thu"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="QAQC / inspection / NCR / checklist",
                subject="QA/QC và nghiệm thu kết cấu thép",
                problem="hồ sơ và hiện trường dễ lệch nhau nếu tiêu chí nghiệm thu, bằng chứng kiểm tra và trách nhiệm xử lý NCR không rõ",
                objects=("ITP", "checklist", "bản vẽ", "tiêu chuẩn nghiệm thu", "ảnh bằng chứng", "NCR"),
                risks=("lọt lỗi sang công đoạn sau", "tranh cãi nghiệm thu", "sửa lỗi tốn chi phí", "ảnh hưởng uy tín nhà máy"),
                causes=("checklist quá chung", "thiếu ảnh hoặc số đo", "chưa khóa điểm hold point", "phân quyền phê duyệt chưa rõ"),
                actions=("xác định tiêu chí pass/fail trước khi kiểm tra", "gắn ảnh, số đo và mã cấu kiện vào hồ sơ", "phân loại NCR theo mức độ ảnh hưởng", "đóng vòng lặp hành động khắc phục"),
                signs=("thiếu chữ ký kiểm tra", "số đo không truy xuất được", "NCR lặp lại ở cùng công đoạn"),
                hashtags=("#QAQC", "#Inspection", "#NCR", "#QualityControl"),
            )

        return TopicProfile(
            topic=title,
            normalized=normalized,
            domain="general manufacturing",
            subject="sản xuất kết cấu thép",
            problem=f"cần biến chủ đề {title} thành hành động cụ thể tại xưởng thay vì chỉ nhắc khẩu hiệu chung",
            objects=("vật tư", "nhân sự", "máy móc", "bản vẽ", "tiêu chuẩn", "tiến độ"),
            risks=("lỗi lặp lại", "mất năng suất", "tăng chi phí", "chậm bàn giao"),
            causes=("quy trình chưa rõ", "thiếu dữ liệu kiểm tra", "trách nhiệm giữa các công đoạn chưa được chuẩn hóa"),
            actions=("xác định tiêu chí kiểm soát theo chủ đề", "giao người chịu trách nhiệm", "đo chỉ số trước và sau cải tiến", "chuẩn hóa thành SOP hoặc checklist"),
            signs=("thông tin truyền miệng", "cùng lỗi xuất hiện nhiều lần", "kết quả phụ thuộc kinh nghiệm cá nhân"),
            hashtags=("#SteelFabrication", "#Manufacturing", "#ProcessImprovement", "#DigitalFactory"),
        )

    def _has(self, normalized: str, *needles: str) -> bool:
        return any(needle in normalized for needle in needles)

    def _normalize(self, text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text.lower())
        no_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
        no_marks = no_marks.replace("đ", "d")
        return re.sub(r"\s+", " ", no_marks).strip()

    def _welding_problem(self, normalized: str) -> str:
        if "ro khi" in normalized or "porosity" in normalized:
            return "rỗ khí mối hàn làm giảm độ tin cậy nghiệm thu vì bề mặt, khí bảo vệ và thông số hàn MIG chưa được kiểm soát đồng bộ"
        if "fit up" in normalized or "fitup" in normalized:
            return "sai khe hở fit-up khiến đường hàn khó đạt kích thước, dễ phải sửa và ảnh hưởng nghiệm thu cấu kiện"
        return "chất lượng mối hàn không ổn định khi chuẩn bị mép, fit-up, thông số hàn và kiểm tra QA/QC chưa đi cùng nhau"

    def _maintenance_problem(self, normalized: str) -> str:
        if "dong co" in normalized and ("qua nhiet" in normalized or "may nen" in normalized):
            return "động cơ máy nén khí quá nhiệt làm tăng nguy cơ dừng máy, cháy cuộn dây và thiếu khí nén cho các công đoạn sản xuất"
        return "thiết bị xưởng phát sinh lỗi khi bảo trì phòng ngừa, đo tải và điều kiện vận hành chưa được kiểm soát theo lịch"


class TopicAwareBuiltInBuilder:
    def __init__(self, output_type: str):
        self.output_type = output_type
        self.classifier = TopicClassifier()

    def build(self, topic: str = "", context: str = "") -> str:
        profile = self.classifier.classify(topic)
        return getattr(self, f"_build_{self.output_type}")(profile)

    def _build_facebook(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"Hook: {p.topic} không phải là khẩu hiệu; nó phải nhìn thấy được trong từng vị trí làm việc.",
                "",
                f"Vấn đề: {p.problem}.",
                "",
                "Dấu hiệu nhận biết:",
                *self._bullets(p.signs),
                "",
                "Nguyên nhân gốc:",
                *self._bullets(p.causes),
                "",
                "Giải pháp:",
                *self._bullets(p.actions),
                "",
                f"Điều học được: {p.subject} chỉ bền khi được đo bằng an toàn, năng suất, chất lượng và mức giảm lãng phí.",
                "",
                f"Hành động: Chọn một khu vực trong xưởng, kiểm tra {self._join(p.objects[:3])}, ghi ảnh trước/sau và chốt người chịu trách nhiệm trong ca.",
                "",
                "Hashtags: " + " ".join(self._hashtags(p)),
            ]
        )

    def _build_tiktok(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"Hook 3 seconds: Quay cận cảnh {p.signs[0]} và nói: \"Đây là lý do {p.topic} phải được kiểm soát ngay trong xưởng.\"",
                "",
                "Scene-by-scene script:",
                f"1. Mở đầu tại xưởng kết cấu thép, chỉ vào {p.objects[0]} và {p.objects[1]}.",
                f"2. Cho thấy vấn đề: {p.problem}.",
                f"3. Cắt nhanh sang dấu hiệu: {p.signs[1]}.",
                f"4. Supervisor/QA kiểm tra nguyên nhân: {p.causes[0]}.",
                f"5. Đội xưởng thực hiện: {p.actions[0]}.",
                f"6. Kết cảnh bằng bảng checklist đã tick và khu vực sạch, an toàn, đúng luồng.",
                "",
                "Voiceover:",
                f"Muốn {p.subject} hiệu quả, đừng chỉ nhắc nhở. Hãy nhìn dấu hiệu, hỏi nguyên nhân gốc, rồi biến thành hành động đo được.",
                "",
                "Text overlay:",
                f"{p.domain} | An toàn | Năng suất | Giảm lãng phí",
                "",
                "Ending CTA: Theo dõi LUCID AUTO để biến kiến thức xưởng thành checklist hành động.",
            ]
        )

    def _build_video(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"English video prompt: Create a 30-second cinematic industrial video about {p.topic} in a steel fabrication workshop.",
                "",
                "Visual scenes:",
                f"- Opening: wide shot of a steel fabrication workshop with beams, plates, tools, marked walkways, PPE workers, welding bays, and QA/QC boards.",
                f"- Scene 1: close-up of {p.objects[0]} and {p.objects[1]} showing the practical issue: {p.problem}.",
                f"- Scene 2: supervisor and worker wearing helmet, gloves, safety glasses, and reflective vest inspect {p.signs[0]}.",
                f"- Scene 3: team performs corrective action: {p.actions[0]}.",
                f"- Ending: clean organized workstation, signed checklist, safe walking path, and improved production flow.",
                "",
                "Camera movement: slow gimbal push-in from the workshop entrance, handheld close-up on tools and steel parts, overhead tracking shot along the production flow, final stable hero shot.",
                "",
                f"Industrial steel fabrication context: include steel structures, semi-finished parts, material tags, machinery, PPE, realistic workshop lighting, QA/QC inspection details, and {p.domain} cues.",
                "",
                "Clear opening and ending: begin with the visible workshop problem and end with verified safe, productive, standardized work.",
            ]
        )

    def _build_image(self, p: TopicProfile) -> str:
        detail_label = self._visual_detail_label(p)
        return "\n".join(
            [
                f"English image prompt: Industrial poster style image about {p.topic}.",
                "",
                f"Clear subject: a steel fabrication workshop team applying {p.subject}, with the main focus on {p.objects[0]}, {p.objects[1]}, and {p.objects[2]}.",
                "",
                f"Workshop context: structural steel beams, semi-finished components, machinery, marked storage zones, tool boards, PPE workers, QA/QC checklist board, realistic factory lighting.",
                "",
                f"{detail_label}: show {p.actions[0]}, visible labels, organized work area, safe walkway, inspection tags, and evidence of {p.domain}.",
                "",
                "Style: clean industrial poster, realistic proportions, sharp focus, professional Vietnamese steel factory environment, no fantasy elements, no random unrelated defects.",
            ]
        )

    def _build_seo(self, p: TopicProfile) -> str:
        keywords = self._keywords(p)
        return "\n".join(
            [
                f"SEO title: {p.topic}: cách kiểm soát hiệu quả trong xưởng kết cấu thép",
                "",
                f"Meta description: Hướng dẫn thực tế về {p.topic}, tập trung vào {self._join(p.objects[:3])}, an toàn, năng suất, chất lượng và hành động chuẩn hóa tại xưởng.",
                "",
                "Keywords:",
                *self._bullets(keywords),
                "",
                "Short article outline:",
                f"1. {p.topic} là gì trong bối cảnh xưởng kết cấu thép?",
                f"2. Vấn đề thường gặp: {p.problem}.",
                f"3. Dấu hiệu nhận biết tại hiện trường: {self._join(p.signs[:3])}.",
                f"4. Nguyên nhân gốc cần kiểm tra: {self._join(p.causes[:3])}.",
                f"5. Giải pháp và checklist hành động: {self._join(p.actions[:3])}.",
                "6. Cách đo hiệu quả bằng chất lượng, an toàn, chi phí và tiến độ.",
                "",
                f"Topic-related search intent: Người tìm kiếm muốn biết cách áp dụng {p.topic} vào công việc thật, có checklist rõ ràng, tránh lỗi lặp lại và cải thiện hiệu quả xưởng.",
            ]
        )

    def _build_hashtags(self, p: TopicProfile) -> str:
        return "\n".join(self._hashtags(p))

    def _build_approval(self, p: TopicProfile) -> str:
        checks = (
            f"[ ] Topic relevance: nội dung nêu rõ {p.topic} và không kéo sang lỗi không liên quan.",
            f"[ ] Quality: có tiêu chí kiểm soát cho {self._join(p.objects[:3])}.",
            f"[ ] Safety: nhận diện rủi ro chính như {p.risks[0]}.",
            f"[ ] Productivity: có hành động giảm lãng phí hoặc thời gian chờ: {p.actions[0]}.",
            f"[ ] Cost: chỉ ra cách giảm sửa lỗi, dừng máy hoặc làm lại theo đúng chủ đề.",
            f"[ ] Schedule: có bước giúp tránh trễ tiến độ do {p.problem}.",
            f"[ ] Standardization: chuyển bài học thành SOP, checklist hoặc điểm kiểm tra theo ca.",
            f"[ ] Scalability: có thể nhân rộng sang tổ/line/khu vực khác trong xưởng kết cấu thép.",
        )
        return "\n".join([f"Approval checklist for: {p.topic}", "", *checks])

    def _hashtags(self, p: TopicProfile) -> list[str]:
        topic_tags = [self._hashtag_from_word(word) for word in self._topic_words(p.topic)]
        tags = [*BASE_HASHTAGS, *p.hashtags, *topic_tags]
        deduped = []
        for tag in tags:
            if tag and tag not in deduped:
                deduped.append(tag)
        return deduped[:14]

    def _keywords(self, p: TopicProfile) -> tuple[str, ...]:
        return (
            p.topic,
            p.subject,
            p.domain,
            *p.objects[:4],
            *p.risks[:2],
            "xưởng kết cấu thép",
            "checklist cải tiến",
        )

    def _visual_detail_label(self, p: TopicProfile) -> str:
        if p.domain.startswith("5S"):
            return "Safety and 5S details"
        if p.domain.startswith("QAQC"):
            return "Safety and QAQC details"
        return "Safety and workshop control details"

    def _topic_words(self, topic: str) -> list[str]:
        words = re.findall(r"[\wÀ-ỹ]+", topic)
        stopwords = {"trong", "cua", "của", "cho", "voi", "với", "the", "and", "may", "máy"}
        return [word for word in words if len(word) >= 3 and word.lower() not in stopwords]

    def _hashtag_from_word(self, word: str) -> str:
        normalized = unicodedata.normalize("NFD", word)
        ascii_word = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        ascii_word = ascii_word.replace("đ", "d").replace("Đ", "D")
        cleaned = re.sub(r"[^A-Za-z0-9]", "", ascii_word)
        if not cleaned:
            return ""
        return f"#{cleaned[:1].upper()}{cleaned[1:]}"

    def _bullets(self, values: tuple[str, ...]) -> list[str]:
        return [f"- {value}" for value in values]

    def _join(self, values: tuple[str, ...]) -> str:
        return ", ".join(values)
