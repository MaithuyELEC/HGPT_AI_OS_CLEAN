from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class GeneralDomainDefinition:
    key: str
    aliases: tuple[str, ...]
    writer_cls: type["GeneralDomainWriter"]


@dataclass(frozen=True)
class GeneralTopicBrief:
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


@dataclass(frozen=True)
class DomainBriefSeed:
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]
    hashtags: tuple[str, ...]


class GeneralTextTools:
    @staticmethod
    def normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFD", (text or "").lower())
        value = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
        value = value.replace("đ", "d")
        return re.sub(r"[^a-z0-9]+", " ", value).strip()

    @staticmethod
    def contains(normalized: str, term: str) -> bool:
        normalized_term = GeneralTextTools.normalize(term)
        if not normalized_term:
            return False
        pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
        return re.search(pattern, normalized) is not None

    @staticmethod
    def join(values: tuple[str, ...]) -> str:
        return ", ".join(values)

    @staticmethod
    def topic_words(topic: str) -> list[str]:
        stopwords = {
            "cach",
            "cách",
            "trong",
            "cua",
            "của",
            "cho",
            "voi",
            "với",
            "hoc",
            "học",
            "day",
            "dạy",
            "quan",
            "quản",
            "the",
            "and",
        }
        words = re.findall(r"[\wÀ-ỹ]+", topic or "")
        return [word for word in words if len(word) >= 3 and word.lower() not in stopwords]

    @staticmethod
    def hashtag(word: str) -> str:
        normalized = unicodedata.normalize("NFD", word)
        value = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        value = value.replace("đ", "d").replace("Đ", "D")
        value = re.sub(r"[^A-Za-z0-9]", "", value)
        return f"#{value[:1].upper()}{value[1:]}" if value else ""


class GeneralTopicClassifier:
    def classify_topic(self, topic: str) -> GeneralDomainDefinition:
        normalized = GeneralTextTools.normalize(topic)
        best: tuple[int, GeneralDomainDefinition] | None = None
        for definition in GENERAL_DOMAIN_DEFINITIONS:
            score = sum(
                1 for alias in definition.aliases if GeneralTextTools.contains(normalized, alias)
            )
            if score and (best is None or score > best[0]):
                best = (score, definition)
        return best[1] if best is not None else LIFESTYLE_DOMAIN

    def is_general_topic(self, topic: str) -> bool:
        normalized = GeneralTextTools.normalize(topic)
        return any(
            GeneralTextTools.contains(normalized, alias)
            for definition in GENERAL_DOMAIN_DEFINITIONS
            for alias in definition.aliases
        )

    def classify(self, brief: GeneralTopicBrief) -> GeneralDomainDefinition:
        return self.classify_topic(" ".join((brief.topic, brief.domain, brief.subject)))


GeneralDomainClassifier = GeneralTopicClassifier


class GeneralDomainRouter:
    def __init__(self) -> None:
        self.classifier = GeneralTopicClassifier()

    def can_handle(self, topic: str) -> bool:
        return self.classifier.is_general_topic(topic)

    def build(self, channel: str, topic_or_brief: str | GeneralTopicBrief) -> str:
        if isinstance(topic_or_brief, GeneralTopicBrief):
            brief = topic_or_brief
            definition = self.classifier.classify(brief)
        else:
            definition = self.classifier.classify_topic(topic_or_brief)
            brief = definition.writer_cls.make_brief(topic_or_brief)

        writer = definition.writer_cls(brief)
        method_name = {
            "approval": "checklist",
            "checklist": "checklist",
            "image_prompt": "image",
            "video_prompt": "video",
        }.get(channel, channel)
        try:
            method = getattr(writer, method_name)
        except AttributeError as exc:
            raise ValueError(f"Unsupported general channel: {channel}") from exc
        return method()


class GeneralDomainWriter:
    key = "lifestyle"
    seed = DomainBriefSeed(
        domain="đời sống",
        subject="thói quen đời sống thực tế",
        problem="cần biến một chủ đề đời sống thành thói quen nhỏ, dễ theo dõi và có kết quả quan sát được",
        objects=("mục tiêu cá nhân", "lịch sinh hoạt", "không gian sống", "thói quen hằng ngày", "ghi chú theo dõi"),
        risks=("bỏ cuộc giữa chừng", "làm theo cảm tính", "khó duy trì đều đặn", "không biết kết quả thay đổi ra sao"),
        causes=("đặt mục tiêu quá rộng", "không chia việc theo ngày", "thiếu cách ghi nhận tiến bộ", "dễ đổi phương pháp liên tục"),
        actions=("chọn một việc nhỏ để bắt đầu trong hôm nay", "ghi lại tình trạng ban đầu", "lặp lại trong bảy ngày", "điều chỉnh dựa trên kết quả quan sát"),
        signs=("khó duy trì sau vài ngày", "không nhớ mình đã làm gì", "kết quả thay đổi không rõ"),
        hashtags=("#DoiSong", "#ThoiQuenTot", "#SongThucTe"),
    )
    setting = "không gian sinh hoạt thật, sáng rõ và gần gũi"
    person = "người thực hiện"
    visual_style = "chân thực, sạch, có cảm giác đời thường"
    color = "màu tự nhiên, sáng vừa, không phô trương"

    def __init__(self, brief: GeneralTopicBrief) -> None:
        self.b = brief

    @classmethod
    def make_brief(cls, topic: str) -> GeneralTopicBrief:
        seed = cls.seed
        clean_topic = (topic or "").strip() or seed.subject
        return GeneralTopicBrief(
            topic=clean_topic,
            domain=seed.domain,
            subject=seed.subject,
            problem=seed.problem,
            objects=seed.objects,
            risks=seed.risks,
            causes=seed.causes,
            actions=seed.actions,
            signs=seed.signs,
            hashtags=seed.hashtags,
        )

    def facebook(self) -> str:
        b = self.b
        return "\n".join(
            [
                "Mở bài",
                f"{b.topic} nên bắt đầu từ một dấu hiệu thật: {b.signs[0]}. Khi nhìn đúng dấu hiệu, người làm bớt chạy theo mẹo rời rạc.",
                "",
                "Bối cảnh",
                f"Trong {b.domain}, trọng tâm là {b.subject}. Vấn đề chính là {b.problem}.",
                "",
                "Điều cần hiểu",
                f"Hãy theo dõi {GeneralTextTools.join(b.objects[:4])}. Nếu bỏ qua các yếu tố này, rủi ro dễ gặp là {b.risks[0]} và {b.risks[1]}.",
                "",
                "Cách làm",
                *[f"- {action}" for action in b.actions[:4]],
                "",
                "Sai lầm thường gặp",
                f"- Chỉ chú ý {b.objects[0]} mà quên {b.objects[1]}.",
                f"- Thấy {b.signs[0]} nhưng lại đổi cách làm quá nhanh.",
                f"- Đợi đến khi {b.risks[2]} mới bắt đầu ghi chép.",
                "",
                "Kết lại",
                f"Muốn làm tốt {b.topic}, hãy giữ một cách làm đủ nhỏ để làm đều và đủ rõ để kiểm tra lại.",
                "",
                "Lời mời",
                f"Lưu lại để tự rà soát {b.topic} theo dấu hiệu, nguyên nhân và hành động cụ thể.",
                "",
                " ".join(self._hashtags()),
            ]
        )

    def tiktok(self) -> str:
        b = self.b
        return "\n".join(
            [
                "Mở đầu",
                f"Nếu bạn đang tìm {b.topic}, đừng bắt đầu bằng mười mẹo cùng lúc.",
                "",
                "Gây chú ý",
                f"Hãy nhìn một dấu hiệu trước: {b.signs[0]}. Dấu hiệu này thường cho biết {b.causes[0]} đang ảnh hưởng đến kết quả.",
                "",
                "Nội dung chính",
                f"Chọn đúng {b.objects[0]}, kiểm tra {b.objects[1]}, rồi làm một bước nhỏ: {b.actions[0]}.",
                "",
                "Ví dụ nhanh",
                f"Trong một ngày bình thường, bạn chỉ cần ghi lại {b.signs[0]} trước khi làm và so sánh lại sau khi đã {b.actions[0]}. Nếu kết quả chưa tốt, xem tiếp {b.causes[1]} thay vì đổi toàn bộ kế hoạch.",
                "",
                "Điểm nhớ",
                f"Điều cần tránh là {b.risks[0]}. Muốn tránh nó, hãy ghi lại kết quả sau mỗi lần làm thay vì đoán bằng cảm giác. Một thay đổi nhỏ nhưng đều thường đáng tin hơn một kế hoạch quá lớn.",
                "",
                "Kết thúc",
                f"{b.topic} dễ hơn khi bạn quan sát thật, làm ít nhưng đều, rồi điều chỉnh theo kết quả.",
            ]
        )

    def seo(self) -> str:
        b = self.b
        return "\n".join(
            [
                f"Tiêu đề SEO: {b.topic} - hướng dẫn thực tế cho {b.domain}",
                f"Mô tả tìm kiếm: Cách bắt đầu {b.topic}, nhận biết dấu hiệu, tránh {b.risks[0]} và áp dụng từng bước dễ theo dõi.",
                "",
                "Từ khóa chính",
                *[f"- {item}" for item in (b.topic, b.subject, b.domain, *b.objects[:4])],
                "",
                "Dàn ý bài viết",
                f"1. Ai nên quan tâm đến {b.topic}?",
                f"2. Dấu hiệu cần nhận biết: {GeneralTextTools.join(b.signs[:3])}.",
                f"3. Nguyên nhân thường gặp: {GeneralTextTools.join(b.causes[:3])}.",
                f"4. Các bước nên làm: {GeneralTextTools.join(b.actions[:4])}.",
                f"5. Cách theo dõi để giảm {b.risks[0]}.",
                "",
                "Câu hỏi thường gặp",
                f"- Bắt đầu từ đâu? {b.actions[0]}.",
                f"- Cần chuẩn bị gì? {GeneralTextTools.join(b.objects[:3])}.",
                f"- Khi nào nên điều chỉnh? Khi thấy {b.signs[0]} hoặc {b.signs[1]}.",
            ]
        )

    def checklist(self) -> str:
        b = self.b
        return "\n".join(
            [
                f"Checklist duyệt nội dung: {b.topic}",
                f"- [ ] Nội dung đúng miền {b.domain} và không kéo sang ngành khác.",
                f"- [ ] Bài có dấu hiệu cụ thể: {GeneralTextTools.join(b.signs[:3])}.",
                f"- [ ] Bài có nguyên nhân phù hợp: {GeneralTextTools.join(b.causes[:3])}.",
                f"- [ ] Bài có hành động rõ: {GeneralTextTools.join(b.actions[:4])}.",
                f"- [ ] Bài nêu rủi ro thực tế: {GeneralTextTools.join(b.risks[:3])}.",
                "- [ ] Giọng viết tự nhiên, không giống văn mẫu cũ.",
                "- [ ] Có thể dùng riêng cho bài đăng, video, tìm kiếm và prompt hình ảnh.",
            ]
        )

    def image(self) -> str:
        b = self.b
        return "\n".join(
            [
                f"Prompt Gemini tạo ảnh: {b.topic}",
                f"Chủ thể - {b.subject}, thấy rõ {GeneralTextTools.join(b.objects[:3])}",
                f"Bối cảnh - {self.setting}, có dấu hiệu {GeneralTextTools.join(b.signs[:2])}",
                f"Hành động - {self.person} đang {b.actions[0]}",
                f"Bố cục - tiền cảnh là {b.objects[0]}, trung cảnh là thao tác chính, hậu cảnh hỗ trợ đúng miền {b.domain}",
                "Ánh sáng - ánh sáng tự nhiên, rõ chi tiết, không gắt",
                "Góc quay - ngang tầm mắt, có một khung cận cảnh để thấy chi tiết quan trọng",
                "Ống kính - cảm giác 35mm cho bối cảnh và 85mm cho chi tiết",
                f"Chất liệu - thể hiện đúng bề mặt thật của {GeneralTextTools.join(b.objects[:3])}",
                f"Màu sắc - {self.color}",
                f"Cảm xúc - {self.visual_style}",
                "Chi tiết cần tránh - chữ sai tiếng Việt, tay méo, vật thể không liên quan, chi tiết giả, hình mờ",
                "Tỷ lệ khung hình - 4:5",
                "Chất lượng - ảnh chân thực, sắc nét, sẵn dùng cho Gemini",
            ]
        )

    def video(self) -> str:
        b = self.b
        return "\n".join(
            [
                f"Prompt Veo tạo video: {b.topic}",
                f"Mở đầu - khung hình đầu cho thấy {b.signs[0]} trong {self.setting}.",
                f"Cảnh một - {self.person} kiểm tra {b.objects[0]} và {b.objects[1]} bằng thao tác chậm, dễ hiểu.",
                f"Cảnh hai - chuyển sang nguyên nhân {b.causes[0]}, đặt cạnh hành động {b.actions[0]}.",
                f"Cảnh ba - kết quả sau khi làm đúng, nhấn vào việc giảm {b.risks[0]}.",
                "Góc quay - xen kẽ toàn cảnh, trung cảnh thao tác và cận cảnh chi tiết chính.",
                "Ánh sáng - tự nhiên, rõ vật thể, màu giữ trung thực.",
                f"Lời thoại - giọng bình tĩnh, nói trực tiếp cho {self.person}, câu ngắn và dễ nhớ.",
                f"Phụ đề - {b.topic} | dấu hiệu | nguyên nhân | bước làm | kiểm tra lại",
                "Âm thanh - nền nhẹ, ưu tiên âm thanh thật của bối cảnh.",
                f"Kết thúc - hiển thị kết quả cạnh ghi chú nhắc lại {b.actions[0]}.",
                "Chi tiết cần tránh - chữ méo, tay thừa, vật thể sai ngữ cảnh, chuyển động giả, thông tin lan man.",
            ]
        )

    def hashtags(self) -> str:
        return "\n".join(self._hashtags())

    def _hashtags(self) -> list[str]:
        tags = ["#MaithuyELEC", "#LucidAuto", "#KienThucThucTe", *self.b.hashtags]
        tags.extend(GeneralTextTools.hashtag(word) for word in GeneralTextTools.topic_words(self.b.topic))
        deduped = []
        for tag in tags:
            if tag and tag not in deduped:
                deduped.append(tag)
        return deduped[:14]


class GardeningWriter(GeneralDomainWriter):
    key = "gardening"
    seed = DomainBriefSeed(
        domain="làm vườn",
        subject="chăm sóc cây và rau tại nhà",
        problem="cần kiểm soát đất, nước, ánh sáng, dinh dưỡng và sâu bệnh để cây khỏe theo mùa",
        objects=("đất trồng", "nước tưới", "ánh sáng", "phân hữu cơ", "lá và rễ", "sâu bệnh"),
        risks=("cây vàng lá", "thối rễ", "rau kém phát triển", "mất mùa nhỏ tại nhà"),
        causes=("tưới quá nhiều hoặc quá ít", "đất bí và thoát nước kém", "thiếu nắng trực tiếp", "bón phân sai thời điểm"),
        actions=("kiểm tra độ ẩm đất trước khi tưới", "đặt cây ở nơi có nắng phù hợp", "tỉa lá hỏng và làm tơi mặt đất", "bón phân nhẹ theo giai đoạn"),
        signs=("lá vàng hoặc rũ xuống", "đất luôn ẩm và có mùi", "cây ít chồi mới"),
        hashtags=("#LamVuon", "#ChamSocCay", "#TrongRauSach", "#MaiVang"),
    )
    setting = "ban công, sân nhà hoặc vườn nhỏ có ánh sáng tự nhiên"
    person = "người chăm cây"
    visual_style = "tươi sáng, gần gũi, thấy rõ sức sống của cây"
    color = "xanh lá, nâu đất, vàng hoa tự nhiên"


class CookingWriter(GeneralDomainWriter):
    key = "cooking"
    seed = DomainBriefSeed(
        domain="nấu ăn",
        subject="nấu món Việt tại bếp gia đình",
        problem="cần chọn nguyên liệu đúng, sơ chế sạch, canh lửa, nêm theo thứ tự và giữ vệ sinh thực phẩm",
        objects=("nguyên liệu", "nồi chảo", "gia vị", "nước dùng", "thời gian nấu", "dao thớt sạch"),
        risks=("món bị dai hoặc nát", "vị mặn nhạt lệch", "mất mùi thơm", "không bảo đảm vệ sinh"),
        causes=("sơ chế vội", "để lửa không phù hợp", "nêm quá sớm", "không canh thời gian mềm của nguyên liệu"),
        actions=("chuẩn bị nguyên liệu trước khi bật bếp", "xào hoặc ướp để tạo nền vị", "hạ lửa đúng lúc", "nếm lại trước khi tắt bếp"),
        signs=("món ra nước nhiều", "thịt chưa mềm", "mùi gia vị chưa hòa", "màu món chưa hấp dẫn"),
        hashtags=("#NauAn", "#BoKho", "#BepNha", "#MonViet"),
    )
    setting = "bếp gia đình sạch, có nguyên liệu thật và ánh sáng ấm"
    person = "người nấu"
    visual_style = "ấm, rõ thao tác, kích thích vị giác"
    color = "màu thực phẩm tự nhiên, hơi ấm của bếp"


class HealthWriter(GeneralDomainWriter):
    key = "health"
    seed = DomainBriefSeed(
        domain="sức khỏe đời sống",
        subject="giảm cân và xây dựng thói quen lành mạnh",
        problem="cần cân bằng ăn uống, vận động, giấc ngủ và theo dõi số đo mà không cực đoan",
        objects=("khẩu phần ăn", "lịch vận động", "giấc ngủ", "nước uống", "số đo cơ thể", "mức năng lượng"),
        risks=("tăng cân trở lại", "mệt mỏi", "ăn kiêng quá mức", "mất động lực"),
        causes=("cắt giảm quá nhanh", "thiếu vận động đều", "ngủ ít", "không ghi lại lượng ăn"),
        actions=("giảm khẩu phần từng bước", "đi bộ hoặc tập nhẹ đều đặn", "ngủ đúng giờ hơn", "theo dõi cân nặng theo tuần"),
        signs=("thèm ăn mạnh vào buổi tối", "mệt khi tập", "cân nặng dao động thất thường"),
        hashtags=("#GiamCan", "#SucKhoe", "#AnUongLanhManh", "#VanDong"),
    )
    setting = "góc bếp sạch, bàn ăn đơn giản hoặc không gian tập nhẹ tại nhà"
    person = "người chăm sóc sức khỏe cá nhân"
    visual_style = "điềm tĩnh, tích cực, tránh phóng đại kết quả"
    color = "trắng sạch, xanh dịu, màu thực phẩm tự nhiên"


class EducationWriter(GeneralDomainWriter):
    key = "education"
    seed = DomainBriefSeed(
        domain="giáo dục",
        subject="lộ trình học tiếng Nhật N5",
        problem="người mới cần nắm bảng chữ cái, từ vựng cơ bản, ngữ pháp nền tảng, nghe ngắn và luyện đề đều",
        objects=("hiragana", "katakana", "từ vựng N5", "ngữ pháp N5", "flashcard", "đề luyện ngắn"),
        risks=("quên mặt chữ", "học lệch ngữ pháp", "nghe không kịp", "mất động lực"),
        causes=("không ôn lặp lại", "học quá nhiều mẫu một lúc", "ít nghe phát âm thật", "thiếu mục tiêu theo tuần"),
        actions=("học chắc hiragana và katakana", "ôn từ bằng thẻ nhớ mỗi ngày", "luyện mẫu câu ngắn", "làm đề nhỏ cuối tuần"),
        signs=("nhầm chữ", "đọc câu ngắn chậm", "khó chia thể cơ bản", "làm bài thiếu thời gian"),
        hashtags=("#TiengNhatN5", "#HocTiengNhat", "#JLPTN5", "#TuVungN5"),
    )
    setting = "bàn học gọn, sổ tay, flashcard và màn hình học tập"
    person = "người học"
    visual_style = "rõ ràng, có nhịp học tập, khích lệ nhưng không sáo rỗng"
    color = "trắng, xanh dịu, màu giấy và bút"


class ParentingWriter(GeneralDomainWriter):
    key = "parenting"
    seed = DomainBriefSeed(
        domain="nuôi dạy con",
        subject="đồng hành cùng con trong học tập",
        problem="cha mẹ cần tạo lịch học, lắng nghe cảm xúc, chia nhỏ bài và khen đúng hành vi để con tiến bộ",
        objects=("góc học tập", "lịch học", "bài tập", "cảm xúc của con", "thời gian nghỉ", "lời khen"),
        risks=("con sợ học", "cha mẹ mất kiên nhẫn", "trì hoãn bài tập", "gia đình căng thẳng"),
        causes=("ép học quá lâu", "mục tiêu không rõ", "ít nghỉ giữa giờ", "chỉ nhắc lỗi mà không khen nỗ lực"),
        actions=("chia bài thành đoạn ngắn", "ngồi cùng con trong thời gian đầu", "khen nỗ lực cụ thể", "kết thúc bằng một việc con làm được"),
        signs=("con né bàn học", "dễ cáu khi làm bài", "quên lịch học", "mất tập trung nhanh"),
        hashtags=("#DayConHoc", "#Parenting", "#GiaDinh", "#KyLuatTichCuc"),
    )
    setting = "phòng khách hoặc góc học tập gia đình"
    person = "cha mẹ"
    visual_style = "ấm, tôn trọng, không phán xét"
    color = "màu nhà ở ấm, ánh sáng mềm, đồ dùng học tập vừa đủ"


class PetWriter(GeneralDomainWriter):
    key = "pets"
    seed = DomainBriefSeed(
        domain="chăm sóc thú cưng",
        subject="chăm sóc chó Husky trong gia đình",
        problem="Husky cần vận động đủ, ăn uống phù hợp, chải lông đều và huấn luyện nhất quán",
        objects=("chó Husky", "khẩu phần ăn", "lịch vận động", "bộ lông", "nước uống", "không gian mát"),
        risks=("tăng động", "rụng lông nhiều", "tăng cân", "phá đồ"),
        causes=("đi dạo quá ít", "khẩu phần không cân bằng", "không chải lông định kỳ", "thiếu quy tắc rõ"),
        actions=("cho vận động mỗi ngày", "chia khẩu phần theo tuổi và cân nặng", "chải lông vài lần mỗi tuần", "dạy lệnh cơ bản bằng thưởng"),
        signs=("hú nhiều khi ở một mình", "cào phá đồ", "lông rối hoặc rụng thành mảng", "thở gấp khi trời nóng"),
        hashtags=("#Husky", "#NuoiCho", "#ChamSocThuCung", "#ChoCanh"),
    )
    setting = "nhà ở hoặc công viên thân thiện với thú cưng"
    person = "người nuôi"
    visual_style = "thân thiện, năng động, an toàn cho thú cưng"
    color = "màu lông tự nhiên, xanh công viên, ánh sáng mềm"


class BusinessWriter(GeneralDomainWriter):
    key = "business"
    seed = DomainBriefSeed(
        domain="kinh doanh nhỏ",
        subject="mở và vận hành quán cà phê",
        problem="cần chọn khách hàng mục tiêu, mặt bằng, menu, vốn, nhân sự, vận hành và điểm hòa vốn trước khi khai trương",
        objects=("khách hàng mục tiêu", "mặt bằng", "menu", "vốn đầu tư", "nhân sự", "điểm hòa vốn"),
        risks=("thuê mặt bằng quá sức", "menu khó vận hành", "thiếu vốn dự phòng", "không kéo được khách quay lại"),
        causes=("khảo sát thị trường ít", "không tính giá vốn", "chưa có quy trình vận hành", "marketing khai trương mờ nhạt"),
        actions=("khảo sát khách quanh khu vực", "tính vốn và điểm hòa vốn", "thử menu nhỏ", "chuẩn hóa phục vụ và nhập hàng"),
        signs=("không biết bán cho ai", "chi phí cố định cao", "menu quá rộng", "doanh thu mỗi ngày không được ghi lại"),
        hashtags=("#MoQuanCaPhe", "#KinhDoanhCafe", "#MenuCafe", "#DiemHoaVon"),
    )
    setting = "quán cà phê nhỏ đang chuẩn bị mở cửa, có quầy pha chế và bảng menu thử"
    person = "chủ quán"
    visual_style = "thực tế, năng động, có cảm giác kinh doanh nhỏ"
    color = "nâu cà phê, xanh cây, trắng sạch và ánh sáng ấm"


class FinanceWriter(GeneralDomainWriter):
    key = "finance"
    seed = DomainBriefSeed(
        domain="tài chính cá nhân",
        subject="quản lý tài chính cá nhân",
        problem="cần biết dòng tiền, quỹ dự phòng, mục tiêu, ngân sách và kỷ luật theo dõi trước khi đầu tư",
        objects=("thu nhập", "chi tiêu", "quỹ dự phòng", "ngân sách tháng", "mục tiêu tài chính", "khoản đầu tư"),
        risks=("hết tiền trước cuối tháng", "không có quỹ khẩn cấp", "mua theo cảm xúc", "áp lực nợ"),
        causes=("không ghi dòng tiền", "chi nhỏ nhưng lặp lại nhiều", "thiếu mục tiêu rõ", "đầu tư trước khi có quỹ dự phòng"),
        actions=("ghi thu chi trong một tháng", "tách quỹ dự phòng trước", "đặt giới hạn chi tiêu", "rà soát ngân sách mỗi tuần"),
        signs=("không biết tiền đang đi đâu", "thường dùng tiền dự phòng cho chi tiêu", "lo lắng khi có khoản phát sinh"),
        hashtags=("#TaiChinhCaNhan", "#QuanLyTien", "#TietKiem", "#NganSach"),
    )
    setting = "bàn làm việc với sổ chi tiêu, ứng dụng ngân hàng và biểu đồ đơn giản"
    person = "người quản lý tiền cá nhân"
    visual_style = "rõ số liệu, thận trọng, không hứa lợi nhuận"
    color = "xanh lá nhạt, trắng, đen mực, màu giấy"


class TechnologyWriter(GeneralDomainWriter):
    key = "technology"
    seed = DomainBriefSeed(
        domain="công nghệ",
        subject="ứng dụng công nghệ vào công việc và đời sống",
        problem="cần chọn công cụ phù hợp, bảo vệ dữ liệu, kiểm chứng kết quả và đo hiệu quả thật",
        objects=("thiết bị cá nhân", "ứng dụng", "dữ liệu", "tài khoản", "quy trình làm việc", "kết quả đầu ra"),
        risks=("lộ dữ liệu", "phụ thuộc công cụ", "sai kết quả", "tốn thời gian vì dùng sai cách"),
        causes=("không đọc quyền truy cập", "sao chép kết quả chưa kiểm chứng", "dùng quá nhiều công cụ", "không đo lợi ích"),
        actions=("chọn một nhu cầu cụ thể", "kiểm tra quyền riêng tư", "thử trên dữ liệu không nhạy cảm", "so sánh thời gian trước và sau"),
        signs=("nhiều thao tác lặp lại", "dữ liệu nằm rải rác", "kết quả cần kiểm tra lại bằng tay"),
        hashtags=("#CongNghe", "#AI", "#UngDungSo", "#BaoMatDuLieu"),
    )
    setting = "bàn làm việc với laptop, điện thoại và công cụ số"
    person = "người dùng công nghệ"
    visual_style = "sắc nét, hiện đại, giải thích bằng thao tác thật"
    color = "trắng, than nhạt, xanh công nghệ và ánh sáng màn hình vừa phải"


class TravelWriter(GeneralDomainWriter):
    key = "travel"
    seed = DomainBriefSeed(
        domain="du lịch",
        subject="lên kế hoạch du lịch Đà Lạt",
        problem="cần cân bằng lịch trình, thời tiết, chi phí, phương tiện, chỗ ở và sức khỏe để chuyến đi nhẹ nhàng",
        objects=("lịch trình", "ngân sách", "thời tiết", "phương tiện", "hành lý", "điểm tham quan"),
        risks=("lịch trình quá dày", "phát sinh chi phí", "trễ giờ di chuyển", "mang thiếu đồ ấm"),
        causes=("đặt quá nhiều điểm trong một ngày", "không xem thời tiết", "không tính thời gian di chuyển", "thiếu danh sách hành lý"),
        actions=("chọn ít điểm nhưng đủ thời gian", "dự phòng chi phí và giờ di chuyển", "kiểm tra thời tiết", "chuẩn bị áo ấm và giấy tờ"),
        signs=("lịch không có giờ nghỉ", "chi phí vượt dự kiến", "phải đổi kế hoạch liên tục", "mệt sau ngày đầu"),
        hashtags=("#DuLichDaLat", "#Travel", "#LichTrinh", "#KinhNghiemDuLich"),
    )
    setting = "điểm đến thật tại Đà Lạt với hành lý gọn, bản đồ và bối cảnh địa phương"
    person = "người đi du lịch"
    visual_style = "thoáng, giàu chuyển động, ưu tiên trải nghiệm thật"
    color = "xanh thông, màu trời tự nhiên, trang phục gọn"


class LifestyleWriter(GeneralDomainWriter):
    key = "lifestyle"


LIFESTYLE_DOMAIN = GeneralDomainDefinition(
    key="lifestyle",
    aliases=("lifestyle", "doi song", "thoi quen", "gia dinh", "ca nhan", "song dep"),
    writer_cls=LifestyleWriter,
)


GENERAL_DOMAIN_DEFINITIONS: tuple[GeneralDomainDefinition, ...] = (
    GeneralDomainDefinition(
        key="gardening",
        aliases=("gardening", "lam vuon", "cay", "mai", "hoa mai", "rau sach", "trong rau", "dat trong", "phan bon"),
        writer_cls=GardeningWriter,
    ),
    GeneralDomainDefinition(
        key="cooking",
        aliases=("cooking", "nau an", "nau", "mon an", "bo kho", "bep", "recipe", "cong thuc"),
        writer_cls=CookingWriter,
    ),
    GeneralDomainDefinition(
        key="health",
        aliases=("health", "suc khoe", "giam can", "dinh duong", "tap luyen", "ngu ngon", "can nang"),
        writer_cls=HealthWriter,
    ),
    GeneralDomainDefinition(
        key="education",
        aliases=("education", "hoc", "tieng nhat", "nhat n5", "n5", "jlpt", "tieng anh", "english"),
        writer_cls=EducationWriter,
    ),
    GeneralDomainDefinition(
        key="parenting",
        aliases=("parenting", "day con", "day con hoc", "nuoi day con", "lam cha me", "tre em"),
        writer_cls=ParentingWriter,
    ),
    GeneralDomainDefinition(
        key="pets",
        aliases=("pet", "pets", "thu cung", "husky", "cho", "dog", "meo", "nuoi cho"),
        writer_cls=PetWriter,
    ),
    GeneralDomainDefinition(
        key="business",
        aliases=("business", "kinh doanh", "mo quan", "quan ca phe", "ca phe", "cafe", "coffee", "khoi nghiep"),
        writer_cls=BusinessWriter,
    ),
    GeneralDomainDefinition(
        key="finance",
        aliases=("finance", "tai chinh", "quan ly tai chinh", "dau tu", "tiet kiem", "ngan sach", "tien"),
        writer_cls=FinanceWriter,
    ),
    GeneralDomainDefinition(
        key="technology",
        aliases=("technology", "cong nghe", "ung dung", "ai", "phan mem", "du lieu", "tu dong hoa"),
        writer_cls=TechnologyWriter,
    ),
    GeneralDomainDefinition(
        key="travel",
        aliases=("travel", "du lich", "da lat", "lich trinh", "khach san", "di choi"),
        writer_cls=TravelWriter,
    ),
    LIFESTYLE_DOMAIN,
)
