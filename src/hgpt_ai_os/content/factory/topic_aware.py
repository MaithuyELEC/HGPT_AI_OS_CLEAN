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
    "#KetCauThep",
    "#KienThucXuong",
    "#NhaMaySo",
)

GENERAL_BASE_HASHTAGS = (
    "#MaithuyELEC",
    "#LucidAuto",
    "#KienThucThucTe",
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
                hashtags=("#5S", "#Kaizen", "#SanXuatTinhGon", "#XuongKetCauThep"),
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
                hashtags=("#Han", "#HanMIG", "#QAQC", "#KetCauThep"),
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
                hashtags=("#SonPhu", "#PhunBi", "#SonKetCau", "#ChongAnMon"),
            )

        if self._has(normalized, "cau truc", "palang", "pa lang", "crane", "hoist"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="bảo trì cầu trục",
                subject="bảo trì cầu trục trong nhà máy",
                problem="cầu trục phải được kiểm tra phanh, cáp tải, móc cẩu, ray, bánh xe, limit switch và điện điều khiển trước khi vận hành",
                objects=("phanh", "cáp tải", "móc cẩu", "ray", "bánh xe", "limit switch", "điện điều khiển"),
                risks=("mất an toàn nâng hạ", "dừng thiết bị đột xuất", "rơi tải", "hư hỏng ray hoặc bánh xe"),
                causes=("phanh mòn", "cáp tải xước hoặc đứt tao", "limit switch lỗi", "ray lệch hoặc bánh xe mòn"),
                actions=("cô lập nguồn điện", "kiểm tra phanh/cáp/móc/ray", "thử limit switch và dừng khẩn", "ghi nhật ký bảo trì"),
                signs=("tiếng kêu khi di chuyển", "cáp tải xù", "móc cẩu biến dạng", "limit switch không dừng đúng"),
                hashtags=("#BaoTriCauTruc", "#CauTruc", "#ThietBiNang", "#AnToanNangHa"),
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
                hashtags=("#BaoTri", "#MayNenKhi", "#DongCo", "#BaoTriPhongNgua"),
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
                hashtags=("#QAQC", "#KiemTra", "#NCR", "#KiemSoatChatLuong"),
            )

        if self._has(normalized, "nuoi ong", "lay mat", "mat ong", "dan ong", "ong chua"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="nuôi ong lấy mật",
                subject="nuôi ong lấy mật",
                problem="cần giữ đàn ong khỏe, đặt thùng gần nguồn hoa, thu mật đúng thời điểm và bảo quản mật sạch",
                objects=("thùng ong", "nguồn hoa", "ong chúa", "cầu mật", "dụng cụ quay mật", "chai bảo quản"),
                risks=("đàn ong yếu", "mật loãng dễ lên men", "ong bỏ tổ", "mật lẫn tạp chất"),
                causes=("thiếu nguồn hoa", "thu mật quá sớm", "dụng cụ chưa vệ sinh", "không theo dõi sức khỏe đàn"),
                actions=("kiểm đàn định kỳ", "đặt thùng gần nguồn hoa sạch", "chỉ quay mật khi cầu mật vít nắp tốt", "lọc và bảo quản mật trong chai sạch"),
                signs=("ong bay yếu", "cầu mật chưa vít nắp", "đàn thiếu phấn hoặc ong chúa đẻ kém"),
                hashtags=("#NuoiOng", "#MatOng", "#OngChua", "#NguonHoa"),
            )

        if self._has(normalized, "day con", "dien thoai", "tre em", "smartphone"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="dạy con dùng điện thoại",
                subject="dạy con sử dụng điện thoại đúng cách",
                problem="gia đình cần kiểm soát thời lượng, nội dung, an toàn mạng và giấc ngủ mà không biến điện thoại thành cuộc chiến",
                objects=("thời lượng sử dụng", "nội dung phù hợp tuổi", "quy tắc gia đình", "an toàn mạng", "giấc ngủ"),
                risks=("nghiện màn hình", "thiếu ngủ", "xem nội dung không phù hợp", "giảm giao tiếp gia đình"),
                causes=("không có quy tắc rõ", "cha mẹ ít đồng hành", "dùng điện thoại để giữ trẻ im lặng"),
                actions=("lập khung giờ dùng", "chọn nội dung cùng con", "dạy an toàn mạng", "đặt điện thoại ngoài phòng ngủ"),
                signs=("con cáu khi bị thu điện thoại", "dùng sát giờ ngủ", "không biết con đang xem gì"),
                hashtags=("#DayCon", "#DienThoai", "#AnToanMang", "#GiaDinh"),
            )

        if " ai " in f" {normalized} " or self._has(normalized, "cong viec", "5 nam", "tuong lai"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="AI và tương lai công việc",
                subject="chuẩn bị kỹ năng làm việc với AI",
                problem="người đi làm cần biết nhiệm vụ nào sẽ được AI hỗ trợ, kỹ năng nào phải học và cách bảo vệ dữ liệu",
                objects=("kỹ năng AI", "tự động hóa việc lặp lại", "dữ liệu công việc", "công cụ mới", "đo hiệu quả"),
                risks=("tụt kỹ năng", "lộ dữ liệu", "phụ thuộc kết quả chưa kiểm chứng", "mất lợi thế nghề nghiệp"),
                causes=("không thử công cụ mới", "không đo hiệu quả", "sao chép đầu ra AI", "thiếu tư duy kiểm chứng"),
                actions=("chọn việc lặp lại để thử AI", "học công cụ mới mỗi tuần", "ẩn dữ liệu nhạy cảm", "đo thời gian tiết kiệm"),
                signs=("công việc lặp lại nhiều", "báo cáo mất thời gian", "đội nhóm chưa có quy tắc dùng AI"),
                hashtags=("#AI", "#CongViec", "#KyNangAI", "#TuDongHoa"),
            )

        if self._has(normalized, "quan ca phe", "ca phe", "cafe", "mo quan", "coffee"):
            return TopicProfile(
                topic=title,
                normalized=normalized,
                domain="mở quán cà phê",
                subject="mở và vận hành quán cà phê nhỏ",
                problem="cần chọn khách hàng mục tiêu, mặt bằng, menu, vốn, nhân sự, marketing và điểm hòa vốn trước khi mở quán",
                objects=("khách hàng mục tiêu", "mặt bằng", "menu", "vốn đầu tư", "nhân sự", "điểm hòa vốn"),
                risks=("thuê mặt bằng quá sức", "menu khó vận hành", "thiếu vốn dự phòng", "không kéo được khách quay lại"),
                causes=("khảo sát thị trường ít", "không tính giá vốn", "chưa có SOP vận hành", "marketing khai trương mờ nhạt"),
                actions=("khảo sát khách", "tính vốn và điểm hòa vốn", "test menu", "chuẩn hóa vận hành", "lập kế hoạch marketing"),
                signs=("không biết bán cho ai", "chi phí cố định cao", "menu quá rộng", "không đo doanh thu mỗi ngày"),
                hashtags=("#MoQuanCaPhe", "#KinhDoanhCafe", "#MenuCafe", "#DiemHoaVon"),
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
            hashtags=("#KetCauThep", "#SanXuat", "#CaiTienQuyTrinh", "#NhaMaySo"),
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
                f"Title: {p.topic}",
                "",
                f"Hook: Nếu {p.topic} chỉ nằm trên giấy, kết quả thực tế sẽ rất dễ lệch.",
                "",
                f"Pain: {p.problem}.",
                "",
                "Story:",
                f"Một đội đang nhìn vào {self._join(p.objects[:3])}. Mọi người đều muốn xử lý nhanh, nhưng các dấu hiệu như {self._join(p.signs[:2])} cho thấy cần kiểm tra kỹ trước khi quyết định.",
                "",
                "Knowledge:",
                f"Điểm cần nhớ: {p.subject} phụ thuộc vào {self._join(p.objects[:4])}. Nguyên nhân thường đến từ {self._join(p.causes[:3])}.",
                "",
                "Practical actions:",
                *self._bullets(p.actions),
                "",
                f"Question: Bạn đang kiểm soát {p.topic} bằng cảm giác hay bằng dữ liệu cụ thể?",
                "",
                f"CTA: Lưu lại và chọn một bước nhỏ hôm nay: kiểm tra {self._join(p.objects[:2])}, ghi nhận dấu hiệu, rồi chốt hành động tiếp theo.",
                "",
                "Hashtags: " + " ".join(self._hashtags(p)),
            ]
        )

    def _build_tiktok(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                "Hook",
                f"{p.topic} nghe đơn giản, nhưng sai một bước là mất tiền, mất thời gian hoặc mất an toàn.",
                "",
                "Curiosity",
                f"Điều nhiều người bỏ qua là {p.signs[0]}. Dấu hiệu nhỏ này thường nói trước một vấn đề lớn hơn.",
                "",
                "Pain",
                f"Nếu xử lý vội, bạn có thể đụng vào {p.risks[0]}, rồi kéo theo {p.risks[1]}.",
                "",
                "Truth",
                f"Muốn làm đúng, đừng bắt đầu bằng lời khuyên chung. Hãy nhìn {p.objects[0]}, kiểm tra {p.objects[1]} và hỏi nguyên nhân thật: {p.causes[0]}.",
                "",
                "One practical tip",
                f"Làm ngay một việc: {p.actions[0]}. Sau đó ghi lại kết quả để lần sau không phải đoán.",
                "",
                "CTA",
                f"Lưu lại nếu bạn đang cần biến {p.topic} thành hành động rõ ràng trong hôm nay.",
            ]
        )

    def _build_video(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"Tiêu đề: {p.topic}",
                "",
                f"Mở đầu: Video dọc 30 giây mở bằng tình huống {p.problem}.",
                "",
                f"Cảnh 1: Tập trung vào {self._join(p.objects[:3])}; làm rõ dấu hiệu {p.signs[0]}.",
                f"Cảnh 2: Nhân vật kiểm tra nguyên nhân {p.causes[0]} và đối chiếu với {p.causes[1]}.",
                f"Cảnh 3: Thực hiện {p.actions[0]}, sau đó ghi nhận kết quả bằng thao tác rõ ràng.",
                "",
                "Góc máy: Cận cảnh chi tiết chính, trung cảnh thao tác con người, khung cuối ổn định để thấy kết quả.",
                "Ánh sáng: Tự nhiên, rõ vật thể, không tối, không làm mất chi tiết quan trọng.",
                f"Lời thoại: \"Đừng xử lý {p.topic} bằng cảm tính. Nhìn dấu hiệu, kiểm tra nguyên nhân, rồi làm một bước có thể đo lại.\"",
                f"Phụ đề: {p.topic} | Dấu hiệu | Nguyên nhân | Hành động | Kiểm tra lại",
                "Âm thanh: Nhịp nền gọn, âm thanh môi trường thật, điểm nhấn nhẹ khi xuất hiện hành động chính.",
                "",
                f"Kết thúc: Hiển thị kết quả sau khi {p.actions[0]} và nhắc lại lợi ích giảm {p.risks[0]}.",
                "CTA: Lưu prompt này để tạo video ngắn có hành động thực tế, không kể lan man.",
            ]
        )

    def _build_image(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"Chủ thể: {p.subject}, trọng tâm là {self._join(p.objects[:3])}",
                f"Bối cảnh: môi trường phù hợp với {p.domain}, có dấu hiệu {self._join(p.signs[:2])}",
                f"Hành động: {p.actions[0]}",
                "Trang phục: phù hợp nghề nghiệp, sạch, an toàn, không phô trương",
                "Ánh sáng: rõ chi tiết, tự nhiên, không quá tối hoặc quá chói",
                "Góc máy: ngang tầm mắt kết hợp cận cảnh chi tiết chính",
                "Ống kính: 35mm cho bối cảnh, 85mm cho chi tiết",
                "Màu sắc: chân thực, cân bằng, ưu tiên màu của vật thể và môi trường thật",
                f"Chi tiết cần có: {self._join((*p.objects[:4], *p.signs[:2]))}",
                "Chi tiết cần tránh: chữ sai tiếng Việt, vật thể méo, chi tiết không liên quan, bối cảnh giả",
                "Phong cách: ảnh tư liệu chân thực, rõ nét, giàu chi tiết, có tính sản xuất",
                "Tỷ lệ: 4:5",
            ]
        )

    def _build_seo(self, p: TopicProfile) -> str:
        keywords = self._keywords(p)
        return "\n".join(
            [
                f"Title: {p.topic}: hướng dẫn thực tế để bắt đầu đúng",
                "",
                f"Meta: Tìm hiểu {p.topic}, các dấu hiệu cần chú ý, nguyên nhân thường gặp và những bước thực tế để giảm {p.risks[0]}.",
                "",
                "Keywords:",
                *self._bullets(keywords),
                "",
                "Outline:",
                f"1. {p.topic} là gì và vì sao đáng quan tâm?",
                f"2. Dấu hiệu chính: {self._join(p.signs[:3])}.",
                f"3. Nguyên nhân cần kiểm tra: {self._join(p.causes[:3])}.",
                f"4. Cách xử lý theo thứ tự: {self._join(p.actions[:3])}.",
                f"5. Cách theo dõi để tránh {p.risks[0]} lặp lại.",
                "",
                "FAQ:",
                f"- Khi nào cần ưu tiên {p.topic}? Khi xuất hiện {p.signs[0]} hoặc {p.signs[1]}.",
                f"- Bước đầu tiên nên làm là gì? {p.actions[0]}.",
                f"- Cần theo dõi yếu tố nào? {self._join(p.objects[:3])}.",
                "",
                f"Conclusion: {p.topic} hiệu quả hơn khi được viết thành dấu hiệu cụ thể, nguyên nhân rõ và hành động có thể kiểm tra lại.",
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
        base = BASE_HASHTAGS if self._is_factory_profile(p) else GENERAL_BASE_HASHTAGS
        tags = [*base, *p.hashtags, *topic_tags]
        deduped = []
        for tag in tags:
            if tag and tag not in deduped:
                deduped.append(tag)
        return deduped[:14]

    def _is_factory_profile(self, p: TopicProfile) -> bool:
        normalized_domain = self.classifier._normalize(p.domain)
        return any(
            token in normalized_domain
            for token in ("steel", "ket cau", "xuong", "factory", "han", "welding", "qaqc", "bao tri", "maintenance", "cau truc", "son", "5s", "kaizen", "lean")
        )

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
