from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from hgpt_ai_os.content.factory.general_domain import (
    GeneralDomainRouter,
    GeneralTopicBrief,
)


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


@dataclass(frozen=True)
class ProblemRule:
    required_terms: tuple[str, ...]
    problem: str


@dataclass(frozen=True)
class TopicProfileDefinition:
    aliases: tuple[str, ...]
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]
    hashtags: tuple[str, ...]
    problem_rules: tuple[ProblemRule, ...] = ()
    use_general_builder: bool = False


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

OUT_OF_SCOPE_ALIASES = (
    "mai",
    "cham soc mai",
    "hoa mai",
    "nau an",
    "cooking",
    "recipe",
    "travel",
    "du lich",
    "finance",
    "tai chinh",
    "thue",
    "gtgt",
    "vat",
    "hoc tieng",
    "japanese",
    "english",
    "husky",
    "dog",
    "nuoi cho",
    "nuoi ong",
    "mat ong",
    "ca phe",
    "cafe",
    "quan ca phe",
    "parenting",
    "day con",
)

TOPIC_PROFILE_CATALOG: tuple[TopicProfileDefinition, ...] = (
    TopicProfileDefinition(
        aliases=("mai", "cham soc mai", "hoa mai", "cay mai"),
        domain="chăm sóc cây mai",
        subject="chăm sóc mai vàng",
        problem="cần kiểm soát nước tưới, ánh sáng, đất trồng, dinh dưỡng và sâu bệnh để cây mai khỏe và ra hoa đúng mùa",
        objects=("cây mai", "đất trồng", "nước tưới", "ánh sáng", "phân bón", "sâu bệnh"),
        risks=("rụng lá", "thối rễ", "ra hoa sai thời điểm", "cây suy yếu sau Tết"),
        causes=("tưới quá nhiều", "đất bí thoát nước kém", "bón phân sai giai đoạn", "không kiểm tra sâu bệnh định kỳ"),
        actions=("đặt cây nơi đủ nắng và thoáng gió", "tưới khi mặt đất se khô", "cắt tỉa cành yếu sau mùa hoa", "bón phân hữu cơ hoặc NPK theo giai đoạn sinh trưởng"),
        signs=("lá vàng hoặc rụng bất thường", "đất luôn ẩm ướt", "nụ ít hoặc nở không đều"),
        hashtags=("#ChamSocMai", "#MaiVang", "#CayCanh", "#LamVuon"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("nuoi cho", "husky"),
        domain="nuôi chó Husky",
        subject="chăm sóc chó Husky",
        problem="Husky cần vận động đủ, ăn uống phù hợp, chải lông đều và được huấn luyện kỷ luật để khỏe mạnh trong môi trường gia đình",
        objects=("chó Husky", "khẩu phần ăn", "lịch vận động", "bộ lông", "không gian sống", "lịch tiêm phòng"),
        risks=("tăng động do thiếu vận động", "rụng lông nhiều", "tăng cân", "phá đồ hoặc hú nhiều"),
        causes=("đi dạo quá ít", "khẩu phần không cân bằng", "không chải lông định kỳ", "thiếu quy tắc huấn luyện nhất quán"),
        actions=("cho vận động hằng ngày bằng đi bộ hoặc chạy nhẹ", "chia khẩu phần theo tuổi và cân nặng", "chải lông vài lần mỗi tuần", "dạy lệnh cơ bản bằng thưởng và lịch cố định"),
        signs=("hú nhiều khi ở một mình", "cào phá đồ", "lông rối hoặc rụng thành mảng", "thở gấp khi trời nóng"),
        hashtags=("#Husky", "#NuoiCho", "#ChamSocThuCung", "#ChoCanh"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("tieng nhat", "nhat n5", "n5"),
        domain="học tiếng Nhật N5",
        subject="lộ trình học tiếng Nhật N5",
        problem="người mới học cần nắm bảng chữ cái, từ vựng cơ bản, ngữ pháp nền tảng, nghe ngắn và luyện đề theo lịch đều đặn",
        objects=("hiragana", "katakana", "từ vựng N5", "ngữ pháp N5", "nghe hội thoại ngắn", "đề luyện JLPT"),
        risks=("quên bảng chữ cái", "học lệch ngữ pháp", "nghe không kịp", "mất động lực vì lịch học quá nặng"),
        causes=("không ôn lặp lại", "học quá nhiều mẫu câu một lúc", "ít nghe phát âm thật", "không có mục tiêu theo tuần"),
        actions=("học chắc hiragana và katakana trước", "ôn từ vựng bằng thẻ nhớ mỗi ngày", "luyện mẫu câu N5 với ví dụ ngắn", "nghe hội thoại chậm và làm đề nhỏ cuối tuần"),
        signs=("nhầm mặt chữ", "khó chia thể cơ bản", "đọc câu ngắn nhưng không hiểu ý", "làm đề bị thiếu thời gian"),
        hashtags=("#TiengNhatN5", "#HocTiengNhat", "#JLPTN5", "#TuVungN5"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("5s", "kaizen", "lean"),
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
    ),
    TopicProfileDefinition(
        aliases=("han", "welding", "weld", "mig", "saw", "fit up", "fitup", "ro khi", "porosity"),
        domain="welding / SAW / MIG / fit-up",
        subject="kiểm soát chất lượng hàn trong kết cấu thép",
        problem="chất lượng mối hàn không ổn định khi chuẩn bị mép, fit-up, thông số hàn và kiểm tra QA/QC chưa đi cùng nhau",
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
        problem_rules=(
            ProblemRule(
                ("ro khi",),
                "rỗ khí mối hàn làm giảm độ tin cậy nghiệm thu vì bề mặt, khí bảo vệ và thông số hàn MIG chưa được kiểm soát đồng bộ",
            ),
            ProblemRule(
                ("porosity",),
                "rỗ khí mối hàn làm giảm độ tin cậy nghiệm thu vì bề mặt, khí bảo vệ và thông số hàn MIG chưa được kiểm soát đồng bộ",
            ),
            ProblemRule(
                ("fit up",),
                "sai khe hở fit-up khiến đường hàn khó đạt kích thước, dễ phải sửa và ảnh hưởng nghiệm thu cấu kiện",
            ),
            ProblemRule(
                ("fitup",),
                "sai khe hở fit-up khiến đường hàn khó đạt kích thước, dễ phải sửa và ảnh hưởng nghiệm thu cấu kiện",
            ),
        ),
    ),
    TopicProfileDefinition(
        aliases=("son", "phun bi", "ban bi", "blasting", "painting", "coating", "be mat"),
        domain="painting / blasting / coating",
        subject="xử lý bề mặt và sơn phủ kết cấu thép",
        problem="lớp phủ khó đạt độ bám dính và tuổi thọ khi bề mặt thép, độ sạch, độ nhám và điều kiện môi trường chưa được kiểm soát",
        objects=("bề mặt thép", "máy phun bi", "sơn lót", "DFT", "độ nhám", "độ ẩm môi trường"),
        risks=("bong tróc sơn", "ăn mòn sớm", "phải xử lý lại bề mặt", "chậm đóng gói và giao hàng"),
        causes=("bề mặt còn bụi muối hoặc dầu", "độ nhám không đạt", "sơn khi nhiệt độ/độ ẩm không phù hợp"),
        actions=("kiểm tra độ sạch và độ nhám trước sơn", "đo DFT theo điểm chuẩn", "cách ly cấu kiện chưa đạt để sửa đúng quy trình"),
        signs=("màu phủ không đều", "DFT lệch vùng", "bề mặt còn bụi hoặc vết dầu"),
        hashtags=("#SonPhu", "#PhunBi", "#SonKetCau", "#ChongAnMon"),
    ),
    TopicProfileDefinition(
        aliases=("cau truc", "palang", "pa lang", "crane", "hoist"),
        domain="bảo trì cầu trục",
        subject="bảo trì cầu trục trong nhà máy",
        problem="cầu trục phải được kiểm tra phanh, cáp tải, móc cẩu, ray, bánh xe, limit switch và điện điều khiển trước khi vận hành",
        objects=("phanh", "cáp tải", "móc cẩu", "ray", "bánh xe", "limit switch", "điện điều khiển"),
        risks=("mất an toàn nâng hạ", "dừng thiết bị đột xuất", "rơi tải", "hư hỏng ray hoặc bánh xe"),
        causes=("phanh mòn", "cáp tải xước hoặc đứt tao", "limit switch lỗi", "ray lệch hoặc bánh xe mòn"),
        actions=("cô lập nguồn điện", "kiểm tra phanh/cáp/móc/ray", "thử limit switch và dừng khẩn", "ghi nhật ký bảo trì"),
        signs=("tiếng kêu khi di chuyển", "cáp tải xù", "móc cẩu biến dạng", "limit switch không dừng đúng"),
        hashtags=("#BaoTriCauTruc", "#CauTruc", "#ThietBiNang", "#AnToanNangHa"),
    ),
    TopicProfileDefinition(
        aliases=("bao tri", "dong co", "motor", "may nen", "compressor", "qua nhiet", "fault"),
        domain="maintenance / motor / compressor / machine fault",
        subject="bảo trì thiết bị xưởng kết cấu thép",
        problem="thiết bị xưởng phát sinh lỗi khi bảo trì phòng ngừa, đo tải và điều kiện vận hành chưa được kiểm soát theo lịch",
        objects=("động cơ", "máy nén khí", "ổ bi", "quạt làm mát", "lọc gió", "tủ điện", "dòng tải"),
        risks=("dừng máy đột xuất", "giảm áp khí cho dây chuyền", "cháy cuộn dây động cơ", "tăng chi phí sửa chữa và chậm tiến độ"),
        causes=("lọc gió bẩn hoặc thông gió kém", "quá tải kéo dài", "ổ bi thiếu bôi trơn", "điện áp hoặc dòng tải bất thường"),
        actions=("đo nhiệt độ vỏ động cơ và dòng tải theo ca", "vệ sinh lọc gió, kiểm tra quạt và đường thông gió", "lập lịch bảo trì phòng ngừa cho máy nén khí", "dừng máy khi vượt ngưỡng nhiệt cho phép"),
        signs=("vỏ động cơ nóng bất thường", "máy nén khí chạy lâu không nghỉ", "áp suất tụt hoặc tiếng ồn ổ bi tăng"),
        hashtags=("#BaoTri", "#MayNenKhi", "#DongCo", "#BaoTriPhongNgua"),
        problem_rules=(
            ProblemRule(
                ("dong co", "qua nhiet"),
                "động cơ máy nén khí quá nhiệt làm tăng nguy cơ dừng máy, cháy cuộn dây và thiếu khí nén cho các công đoạn sản xuất",
            ),
            ProblemRule(
                ("dong co", "may nen"),
                "động cơ máy nén khí quá nhiệt làm tăng nguy cơ dừng máy, cháy cuộn dây và thiếu khí nén cho các công đoạn sản xuất",
            ),
        ),
    ),
    TopicProfileDefinition(
        aliases=("qaqc", "qc", "inspection", "kiem tra", "ncr", "checklist", "nghiem thu"),
        domain="QAQC / inspection / NCR / checklist",
        subject="QA/QC và nghiệm thu kết cấu thép",
        problem="hồ sơ và hiện trường dễ lệch nhau nếu tiêu chí nghiệm thu, bằng chứng kiểm tra và trách nhiệm xử lý NCR không rõ",
        objects=("ITP", "checklist", "bản vẽ", "tiêu chuẩn nghiệm thu", "ảnh bằng chứng", "NCR"),
        risks=("lọt lỗi sang công đoạn sau", "tranh cãi nghiệm thu", "sửa lỗi tốn chi phí", "ảnh hưởng uy tín nhà máy"),
        causes=("checklist quá chung", "thiếu ảnh hoặc số đo", "chưa khóa điểm hold point", "phân quyền phê duyệt chưa rõ"),
        actions=("xác định tiêu chí pass/fail trước khi kiểm tra", "gắn ảnh, số đo và mã cấu kiện vào hồ sơ", "phân loại NCR theo mức độ ảnh hưởng", "đóng vòng lặp hành động khắc phục"),
        signs=("thiếu chữ ký kiểm tra", "số đo không truy xuất được", "NCR lặp lại ở cùng công đoạn"),
        hashtags=("#QAQC", "#KiemTra", "#NCR", "#KiemSoatChatLuong"),
    ),
    TopicProfileDefinition(
        aliases=("nuoi ong", "lay mat", "mat ong", "dan ong", "ong chua"),
        domain="nuôi ong lấy mật",
        subject="nuôi ong lấy mật",
        problem="cần giữ đàn ong khỏe, đặt thùng gần nguồn hoa, thu mật đúng thời điểm và bảo quản mật sạch",
        objects=("thùng ong", "nguồn hoa", "ong chúa", "cầu mật", "dụng cụ quay mật", "chai bảo quản"),
        risks=("đàn ong yếu", "mật loãng dễ lên men", "ong bỏ tổ", "mật lẫn tạp chất"),
        causes=("thiếu nguồn hoa", "thu mật quá sớm", "dụng cụ chưa vệ sinh", "không theo dõi sức khỏe đàn"),
        actions=("kiểm đàn định kỳ", "đặt thùng gần nguồn hoa sạch", "chỉ quay mật khi cầu mật vít nắp tốt", "lọc và bảo quản mật trong chai sạch"),
        signs=("ong bay yếu", "cầu mật chưa vít nắp", "đàn thiếu phấn hoặc ong chúa đẻ kém"),
        hashtags=("#NuoiOng", "#MatOng", "#OngChua", "#NguonHoa"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("day con", "dien thoai", "tre em", "smartphone"),
        domain="dạy con dùng điện thoại",
        subject="dạy con sử dụng điện thoại đúng cách",
        problem="gia đình cần kiểm soát thời lượng, nội dung, an toàn mạng và giấc ngủ mà không biến điện thoại thành cuộc chiến",
        objects=("thời lượng sử dụng", "nội dung phù hợp tuổi", "quy tắc gia đình", "an toàn mạng", "giấc ngủ"),
        risks=("nghiện màn hình", "thiếu ngủ", "xem nội dung không phù hợp", "giảm giao tiếp gia đình"),
        causes=("không có quy tắc rõ", "cha mẹ ít đồng hành", "dùng điện thoại để giữ trẻ im lặng"),
        actions=("lập khung giờ dùng", "chọn nội dung cùng con", "dạy an toàn mạng", "đặt điện thoại ngoài phòng ngủ"),
        signs=("con cáu khi bị thu điện thoại", "dùng sát giờ ngủ", "không biết con đang xem gì"),
        hashtags=("#DayCon", "#DienThoai", "#AnToanMang", "#GiaDinh"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("ai", "cong viec", "5 nam", "tuong lai"),
        domain="AI và tương lai công việc",
        subject="chuẩn bị kỹ năng làm việc với AI",
        problem="người đi làm cần biết nhiệm vụ nào sẽ được AI hỗ trợ, kỹ năng nào phải học và cách bảo vệ dữ liệu",
        objects=("kỹ năng AI", "tự động hóa việc lặp lại", "dữ liệu công việc", "công cụ mới", "đo hiệu quả"),
        risks=("tụt kỹ năng", "lộ dữ liệu", "phụ thuộc kết quả chưa kiểm chứng", "mất lợi thế nghề nghiệp"),
        causes=("không thử công cụ mới", "không đo hiệu quả", "sao chép đầu ra AI", "thiếu tư duy kiểm chứng"),
        actions=("chọn việc lặp lại để thử AI", "học công cụ mới mỗi tuần", "ẩn dữ liệu nhạy cảm", "đo thời gian tiết kiệm"),
        signs=("công việc lặp lại nhiều", "báo cáo mất thời gian", "đội nhóm chưa có quy tắc dùng AI"),
        hashtags=("#AI", "#CongViec", "#KyNangAI", "#TuDongHoa"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("quan ca phe", "ca phe", "cafe", "mo quan", "coffee"),
        domain="mở quán cà phê",
        subject="mở và vận hành quán cà phê nhỏ",
        problem="cần chọn khách hàng mục tiêu, mặt bằng, menu, vốn, nhân sự, marketing và điểm hòa vốn trước khi mở quán",
        objects=("khách hàng mục tiêu", "mặt bằng", "menu", "vốn đầu tư", "nhân sự", "điểm hòa vốn"),
        risks=("thuê mặt bằng quá sức", "menu khó vận hành", "thiếu vốn dự phòng", "không kéo được khách quay lại"),
        causes=("khảo sát thị trường ít", "không tính giá vốn", "chưa có SOP vận hành", "marketing khai trương mờ nhạt"),
        actions=("khảo sát khách", "tính vốn và điểm hòa vốn", "test menu", "chuẩn hóa vận hành", "lập kế hoạch marketing"),
        signs=("không biết bán cho ai", "chi phí cố định cao", "menu quá rộng", "không đo doanh thu mỗi ngày"),
        hashtags=("#MoQuanCaPhe", "#KinhDoanhCafe", "#MenuCafe", "#DiemHoaVon"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("nau an", "cooking", "recipe", "mon an"),
        domain="nấu ăn gia đình",
        subject="nấu ăn thực tế mỗi ngày",
        problem="người nấu cần chọn nguyên liệu phù hợp, sơ chế sạch, kiểm soát nhiệt, nêm nếm theo thứ tự và giữ an toàn thực phẩm",
        objects=("nguyên liệu", "dao thớt", "nồi chảo", "nhiệt độ", "gia vị", "thời gian nấu"),
        risks=("món ăn bị sống hoặc quá chín", "mất vị cân bằng", "lãng phí nguyên liệu", "không bảo đảm vệ sinh"),
        causes=("không chuẩn bị nguyên liệu trước", "để lửa quá lớn", "nêm quá sớm hoặc quá muộn", "không tách đồ sống và đồ chín"),
        actions=("đọc công thức và chuẩn bị nguyên liệu trước khi bật bếp", "sơ chế sạch và tách đồ sống với đồ chín", "kiểm soát lửa theo từng giai đoạn", "nếm lại trước khi tắt bếp và ghi chú lần sau"),
        signs=("món ra nước nhiều", "thức ăn cháy cạnh", "vị quá mặn hoặc nhạt", "nguyên liệu chín không đều"),
        hashtags=("#NauAn", "#Cooking", "#BepNha", "#AnToanThucPham"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("dog", "cho", "nuoi cho", "cham soc cho"),
        domain="chăm sóc chó nuôi",
        subject="nuôi chó trong gia đình",
        problem="người nuôi cần kiểm soát ăn uống, vận động, vệ sinh, tiêm phòng và huấn luyện cơ bản để chó khỏe và sống hòa hợp với gia đình",
        objects=("khẩu phần ăn", "nước uống", "lịch vận động", "vệ sinh", "tiêm phòng", "lệnh cơ bản"),
        risks=("chó tăng cân", "hành vi phá đồ", "bệnh ngoài da", "thiếu kỷ luật khi sống trong nhà"),
        causes=("cho ăn tùy hứng", "ít vận động", "không vệ sinh định kỳ", "huấn luyện thiếu nhất quán"),
        actions=("lập giờ ăn và lượng ăn theo tuổi", "cho vận động hằng ngày", "tắm chải và kiểm tra da lông định kỳ", "dạy lệnh ngắn bằng thưởng tích cực"),
        signs=("chó lười vận động", "gãi nhiều", "ăn thất thường", "khó nghe lệnh cơ bản"),
        hashtags=("#DogCare", "#NuoiCho", "#ThuCung", "#ChamSocCho"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("english", "hoc tieng anh", "tieng anh", "english learning"),
        domain="học tiếng Anh",
        subject="lộ trình học tiếng Anh thực dụng",
        problem="người học cần cân bằng từ vựng, phát âm, nghe, nói, đọc và viết theo mục tiêu giao tiếp hoặc công việc",
        objects=("từ vựng", "phát âm", "nghe", "nói", "đọc", "viết"),
        risks=("học nhiều nhưng không dùng được", "ngại nói", "quên từ nhanh", "phát âm khó nghe"),
        causes=("học rời rạc", "ít luyện nghe thật", "không ôn lặp lại", "thiếu tình huống áp dụng"),
        actions=("chọn một mục tiêu giao tiếp cụ thể", "học từ theo cụm câu", "nghe ngắn mỗi ngày và nhại lại", "viết hoặc nói một đoạn ngắn rồi sửa lỗi"),
        signs=("biết từ nhưng không ghép được câu", "nghe được từng từ nhưng không hiểu ý", "ngại nói trước người khác"),
        hashtags=("#EnglishLearning", "#HocTiengAnh", "#TuVung", "#GiaoTiep"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("parenting", "day con", "nuoi day con", "lam cha me"),
        domain="nuôi dạy con",
        subject="nuôi dạy con trong gia đình",
        problem="cha mẹ cần xây dựng quy tắc rõ, lắng nghe cảm xúc, giữ lịch sinh hoạt ổn định và kỷ luật tích cực theo độ tuổi",
        objects=("quy tắc gia đình", "cảm xúc của con", "giấc ngủ", "thói quen học", "thời gian màn hình", "kỷ luật tích cực"),
        risks=("con phản kháng", "gia đình căng thẳng", "thói quen xấu lặp lại", "cha mẹ mất nhất quán"),
        causes=("quy tắc thay đổi liên tục", "phản ứng bằng la mắng", "thiếu thời gian trò chuyện", "không theo dõi thói quen hằng ngày"),
        actions=("chọn một quy tắc ưu tiên trong tuần", "nói rõ kỳ vọng bằng câu ngắn", "khen hành vi đúng ngay khi xuất hiện", "xem lại lịch ngủ, học và màn hình mỗi ngày"),
        signs=("con dễ cáu", "khó ngủ", "trì hoãn việc học", "tranh cãi khi bị nhắc nhở"),
        hashtags=("#Parenting", "#DayCon", "#GiaDinh", "#KyLuatTichCuc"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("finance", "tai chinh", "dau tu", "etf", "tiet kiem"),
        domain="tài chính cá nhân",
        subject="quản lý tiền và đầu tư cá nhân",
        problem="người mới cần hiểu mục tiêu, khẩu vị rủi ro, quỹ dự phòng, chi phí và kỷ luật theo dõi trước khi đầu tư hoặc phân bổ tiền",
        objects=("mục tiêu tài chính", "quỹ dự phòng", "danh mục ETF", "ngân sách tháng", "khẩu vị rủi ro"),
        risks=("mua theo đám đông", "thiếu tiền dự phòng", "chịu phí cao", "bán hoảng loạn khi thị trường giảm"),
        causes=("không xác định mục tiêu", "không hiểu sản phẩm", "đầu tư bằng tiền cần dùng ngắn hạn", "không ghi lại dòng tiền"),
        actions=("lập quỹ dự phòng trước", "xác định mục tiêu và thời hạn đầu tư", "đọc phí và rủi ro của ETF", "theo dõi danh mục theo tháng thay vì theo cảm xúc"),
        signs=("không biết tiền đang đi đâu", "mua bán vì tin nóng", "lo lắng khi giá biến động", "không có kế hoạch nạp tiền định kỳ"),
        hashtags=("#TaiChinhCaNhan", "#DauTuETF", "#QuanLyTien", "#TietKiem"),
        use_general_builder=True,
    ),
    TopicProfileDefinition(
        aliases=("travel", "du lich", "lich trinh", "di choi"),
        domain="du lịch",
        subject="lên kế hoạch du lịch thực tế",
        problem="người đi du lịch cần cân bằng lịch trình, chi phí, thời tiết, giấy tờ, phương tiện và sức khỏe để chuyến đi ít rủi ro",
        objects=("lịch trình", "ngân sách", "giấy tờ", "phương tiện", "hành lý", "thời tiết"),
        risks=("trễ chuyến", "phát sinh chi phí", "mang thiếu đồ quan trọng", "lịch trình quá dày"),
        causes=("đặt lịch quá sát", "không kiểm tra thời tiết", "không tính thời gian di chuyển", "thiếu danh sách đồ cần mang"),
        actions=("chọn ít điểm nhưng đủ thời gian", "dự phòng chi phí và thời gian di chuyển", "kiểm tra giấy tờ trước ngày đi", "chuẩn bị hành lý theo thời tiết và hoạt động"),
        signs=("lịch trình không có giờ nghỉ", "chi phí vượt dự kiến", "phải đổi kế hoạch liên tục", "thiếu giấy tờ hoặc vật dụng cơ bản"),
        hashtags=("#DuLich", "#Travel", "#LichTrinh", "#KinhNghiemDuLich"),
        use_general_builder=True,
    ),
)


class TopicClassifier:
    def classify(self, topic: str) -> TopicProfile:
        title = (topic or "").strip() or "Cải tiến xưởng sản xuất kết cấu thép"
        normalized = self._normalize(title)

        definition = self.match_definition(title)
        if definition is not None:
            return self._profile_from_definition(title, normalized, definition)

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

    def match_definition(self, topic: str) -> TopicProfileDefinition | None:
        normalized = self._normalize(topic)
        for definition in TOPIC_PROFILE_CATALOG:
            if self._matches_any(normalized, definition.aliases):
                return definition
        return None

    def matches_known_profile(self, topic: str) -> bool:
        return self.match_definition(topic) is not None

    def is_out_of_scope(self, topic: str) -> bool:
        normalized = self._normalize(topic)
        return self._matches_any(normalized, OUT_OF_SCOPE_ALIASES)

    def uses_general_builder(self, topic: str) -> bool:
        definition = self.match_definition(topic)
        return bool(definition and definition.use_general_builder)

    def _profile_from_definition(
        self,
        title: str,
        normalized: str,
        definition: TopicProfileDefinition,
    ) -> TopicProfile:
        return TopicProfile(
            topic=title,
            normalized=normalized,
            domain=definition.domain,
            subject=definition.subject,
            problem=self._select_problem(normalized, definition),
            objects=definition.objects,
            risks=definition.risks,
            causes=definition.causes,
            actions=definition.actions,
            signs=definition.signs,
            hashtags=definition.hashtags,
        )

    def _matches_any(self, normalized: str, aliases: tuple[str, ...]) -> bool:
        return any(self._contains_term(normalized, alias) for alias in aliases)

    def _select_problem(
        self,
        normalized: str,
        definition: TopicProfileDefinition,
    ) -> str:
        for rule in definition.problem_rules:
            if all(
                self._contains_term(normalized, term)
                for term in rule.required_terms
            ):
                return rule.problem
        return definition.problem

    def _contains_term(self, normalized: str, term: str) -> bool:
        normalized_term = self._normalize(term)
        if not normalized_term:
            return False
        pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
        return re.search(pattern, normalized) is not None

    def _normalize(self, text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text.lower())
        no_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
        no_marks = no_marks.replace("đ", "d")
        return re.sub(r"[^a-z0-9]+", " ", no_marks).strip()


class TopicAwareBuiltInBuilder:
    def __init__(self, output_type: str):
        self.output_type = output_type
        self.classifier = TopicClassifier()
        self.general_router = GeneralDomainRouter()

    def build(self, topic: str = "", context: str = "") -> str:
        profile = self.classifier.classify(topic)
        if self.classifier.is_out_of_scope(topic):
            return self._build_engineering_scope_notice(profile.topic)
        if self.general_router.can_handle(topic):
            return self._build_engineering_scope_notice(profile.topic)
        if self.classifier.uses_general_builder(topic):
            return self._build_engineering_scope_notice(profile.topic)
        return getattr(self, f"_build_{self.output_type}")(profile)

    def _build_engineering_scope_notice(self, topic: str) -> str:
        title = (topic or "").strip() or "Chủ đề ngoài phạm vi kỹ thuật"
        lines = [
            f"LUCID AUTO v1.0 Engineering Scope: {title}",
            "",
            "Chủ đề này nằm ngoài phạm vi Engineering AI Platform.",
            "",
            "LUCID AUTO chỉ tạo tài liệu cho:",
            "- Steel Structure",
            "- Mechanical Engineering",
            "- Welding / Fabrication",
            "- QA/QC / NDT",
            "- Maintenance / TPM",
            "- Lean / Kaizen / 5S",
            "- Digital Factory",
            "",
            "Vui lòng nhập một chủ đề kỹ thuật như: lỗi hàn SAW rỗ khí, bu lông neo sai vị trí, máy nén khí quá nhiệt, bạc đạn hỏng, kiểm tra DFT, VT/UT/MT/PT/RT hoặc checklist QA/QC.",
        ]
        if self.output_type == "hashtags":
            return "#LucidAuto #EngineeringAI #MechanicalEngineering #QAQC #Maintenance #Welding"
        if self.output_type == "image":
            return "\n".join([
                "Prompt Gemini tạo ảnh",
                f"Chủ thể: màn hình thông báo phạm vi kỹ thuật LUCID AUTO Engineering AI Platform cho chủ đề {title}",
                "Bối cảnh: văn phòng QA/QC trong xưởng cơ khí, có bản vẽ kỹ thuật và checklist kiểm tra, chủ đề được đánh dấu ngoài phạm vi",
                "Hành động: kỹ sư chọn lại chủ đề thuộc cơ khí, hàn, kết cấu thép hoặc bảo trì",
                "Chi tiết cần tránh: minh họa đời sống, nấu ăn, du lịch, tài chính, thú cưng, cây cảnh",
            ])
        if self.output_type == "video":
            return "\n".join([
                f"Tiêu đề: LUCID AUTO chỉ nhận chủ đề kỹ thuật - {title}",
                "Mở đầu: hiển thị xưởng cơ khí và danh sách phạm vi Engineering AI Platform; chủ đề hiện tại được đánh dấu ngoài phạm vi.",
                "Cảnh 1: kỹ sư loại bỏ chủ đề ngoài ngành khỏi kế hoạch tạo tài liệu.",
                "Cảnh 2: chọn lại chủ đề thuộc welding, QA/QC, maintenance, steel structure hoặc digital factory.",
                "Kết thúc: chỉ tạo SOP, checklist, field handbook hoặc training material kỹ thuật.",
            ])
        return "\n".join(lines)

    def _build_facebook(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                f"Introduction",
                f"{p.topic} cần được biến thành kiến thức dễ hiểu, có hành động rõ và có cách kiểm tra lại trong đời sống thực tế.",
                "",
                "Main knowledge",
                f"{p.problem}. Trọng tâm của chủ đề là {p.subject}, trong đó cần chú ý đến {self._join(p.objects[:4])}.",
                "",
                "Step-by-step actions",
                *self._numbered(p.actions),
                "",
                "Practical advice",
                f"Hãy theo dõi các dấu hiệu như {self._join(p.signs[:3])}. Nếu thấy dấu hiệu lặp lại, quay lại kiểm tra {self._join(p.causes[:3])} trước khi đổi cách làm.",
                "",
                "Common mistakes",
                *self._bullets(
                    tuple(
                        f"Chỉ chú ý đến {item} mà không kiểm tra toàn bộ bối cảnh."
                        for item in p.objects[:3]
                    )
                ),
                "",
                "Conclusion",
                f"Khi {p.topic} được viết thành kiến thức, hành động và dấu hiệu kiểm tra, người đọc có thể áp dụng ngay mà không phụ thuộc vào lời khuyên chung chung.",
                "",
                " ".join(self._hashtags(p)),
            ]
        )

    def _build_tiktok(self, p: TopicProfile) -> str:
        return "\n".join(
            [
                "Mở đầu",
                f"{p.topic} nghe đơn giản, nhưng muốn làm đúng phải nhìn vào dấu hiệu cụ thể trước.",
                "",
                "Khơi mở kiến thức",
                f"Điều nhiều người bỏ qua là {p.signs[0]}. Đây là tín hiệu cho thấy cần kiểm tra {p.objects[0]} và {p.objects[1]}.",
                "",
                "Điểm cần tránh",
                f"Nếu xử lý vội, bạn có thể gặp {p.risks[0]}, rồi kéo theo {p.risks[1]}.",
                "",
                "Cách làm đúng",
                f"Bắt đầu bằng việc {p.actions[0]}, sau đó ghi lại kết quả để biết cách làm có hiệu quả hay không.",
                "",
                "Gợi ý áp dụng",
                f"Mỗi ngày chỉ cần chọn một bước nhỏ liên quan đến {p.topic}, làm đều và kiểm tra lại bằng dấu hiệu thực tế.",
                "",
                "Kết thúc",
                f"Khi hiểu dấu hiệu, nguyên nhân và bước làm, {p.topic} sẽ bớt mơ hồ và dễ áp dụng hơn.",
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
                "Kêu gọi hành động: Lưu quy trình này để tạo video ngắn có hành động thực tế, không kể lan man.",
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
        scale_target = (
            "có thể nhân rộng sang tổ/line/khu vực khác trong xưởng kết cấu thép"
            if self._is_factory_profile(p)
            else "có thể lặp lại thành thói quen, lịch theo dõi hoặc checklist cá nhân"
        )
        checks = (
            f"[ ] Đúng chủ đề: nội dung nêu rõ {p.topic} và không kéo sang lỗi không liên quan.",
            f"[ ] Chất lượng: có tiêu chí kiểm soát cho {self._join(p.objects[:3])}.",
            f"[ ] An toàn: nhận diện rủi ro chính như {p.risks[0]}.",
            f"[ ] Hiệu quả: có hành động giảm lãng phí hoặc thời gian chờ: {p.actions[0]}.",
            f"[ ] Chi phí: chỉ ra cách giảm sửa lỗi, dừng máy hoặc làm lại theo đúng chủ đề.",
            f"[ ] Thời gian: có bước giúp tránh chậm trễ do {p.problem}.",
            f"[ ] Chuẩn hóa: chuyển bài học thành SOP, checklist hoặc điểm kiểm tra theo ca.",
            f"[ ] Nhân rộng: {scale_target}.",
        )
        return "\n".join([f"Checklist duyệt nội dung: {p.topic}", "", *checks])

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
        keywords = (
            p.topic,
            p.subject,
            p.domain,
            *p.objects[:4],
            *p.risks[:2],
        )
        if self._is_factory_profile(p):
            return (*keywords, "xưởng kết cấu thép", "checklist cải tiến")
        return (*keywords, "hướng dẫn thực tế", "checklist theo dõi")

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

    def _numbered(self, values: tuple[str, ...]) -> list[str]:
        return [f"{index}. {value}" for index, value in enumerate(values, start=1)]

    def _join(self, values: tuple[str, ...]) -> str:
        return ", ".join(values)
