from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from hgpt_ai_os.engineering_pipeline.intent import TopicIntent
from hgpt_ai_os.engineering_pipeline.record import EngineeringRecord


@dataclass(frozen=True)
class OfflineEngineeringProfile:
    aliases: tuple[str, ...]
    title: str
    problem: str
    domain: str
    equipment: tuple[str, ...]
    component: tuple[str, ...]
    symptoms: tuple[str, ...]
    working_principle: str
    mechanisms: tuple[str, ...]
    causes: tuple[str, ...]
    consequences: tuple[str, ...]
    inspection: tuple[str, ...]
    measurements: tuple[str, ...]
    tools: tuple[str, ...]
    repair: tuple[str, ...]
    verification: tuple[str, ...]
    prevention: tuple[str, ...]
    lessons: tuple[str, ...]
    mistakes: tuple[str, ...]
    standards: tuple[str, ...]


SAW_POROSITY = OfflineEngineeringProfile(
    aliases=("duong han saw bi ro khi", "saw porosity", "ro khi saw", "saw bi ro khi", "duong han saw"),
    title="Đường hàn SAW bị rỗ khí",
    domain="Hàn kết cấu thép",
    problem=(
        "Đường hàn SAW nhìn đều và đẹp bên ngoài vẫn có thể chứa lỗ khí bên trong hoặc trên bề mặt. "
        "Rỗ khí hình thành khi khí bị giữ lại trong kim loại mối hàn trong lúc đông đặc, thường do thuốc hàn, vật liệu nền, dây hàn hoặc thông số hàn không được kiểm soát đúng."
    ),
    equipment=("máy hàn SAW", "dầm H kết cấu thép", "hệ cấp thuốc hàn", "bộ cấp dây hàn"),
    component=("đường hàn SAW", "kim loại mối hàn", "thuốc hàn", "dây hàn", "bề mặt thép"),
    symptoms=(
        "bề mặt đường hàn xuất hiện lỗ rỗ nhỏ hoặc cụm lỗ li ti",
        "kết quả UT hoặc RT phát hiện lỗ khí bên trong mối hàn",
        "đường hàn nhìn đều nhưng chất lượng bên trong không ổn định",
        "vùng hàn có dấu hiệu nhiễm ẩm, bẩn hoặc hồ quang dao động",
        "mối hàn phải khoan, mài hoặc sửa lại sau kiểm tra không phá hủy",
    ),
    working_principle=(
        "Trong hàn SAW, hồ quang cháy dưới lớp thuốc hàn và kim loại nóng chảy phải thoát khí trước khi đông đặc. "
        "Khi độ ẩm, tạp chất, dây hàn oxy hóa hoặc thông số hàn làm khí sinh ra quá nhiều hoặc thoát không kịp, lỗ khí sẽ bị giữ lại trong mối hàn."
    ),
    mechanisms=(
        "hơi ẩm trong thuốc hàn phân hủy trong vùng hồ quang và tạo khí bị kẹt khi kim loại đông đặc",
        "dầu mỡ, gỉ sét hoặc hơi ẩm trên bề mặt thép sinh khí trong vũng hàn",
        "dây hàn oxy hóa hoặc bảo quản sai làm tăng tạp chất đi vào kim loại hàn",
        "dòng điện, điện áp hoặc tốc độ hàn sai làm vũng hàn đông đặc không ổn định",
        "hồ quang dao động hoặc lớp thuốc phủ không đủ làm vùng hàn bị nhiễm khí",
    ),
    causes=(
        "Thuốc hàn bị ẩm hoặc nhiễm bẩn do bảo quản, sấy và thu hồi không đúng quy trình",
        "Bề mặt thép còn dầu mỡ, gỉ sét, bụi bẩn hoặc hơi ẩm trước khi hàn",
        "Dây hàn bị oxy hóa, bám bẩn hoặc bảo quản không đúng điều kiện",
        "Dòng điện, điện áp hoặc tốc độ hàn không phù hợp với WPS",
        "Hồ quang không ổn định hoặc lớp thuốc hàn phủ không đủ trong quá trình hàn",
    ),
    consequences=(
        "Giảm tiết diện chịu lực thực tế của mối hàn",
        "Giảm khả năng chịu tải, chịu mỏi và độ tin cậy của liên kết hàn",
        "Không đạt kiểm tra UT hoặc RT trong nghiệm thu chất lượng",
        "Phải mài sửa, hàn sửa, tăng chi phí và làm chậm tiến độ giao cấu kiện",
    ),
    inspection=(
        "Kiểm tra tình trạng sấy, bảo quản và thu hồi thuốc hàn trước khi cấp vào máy",
        "Kiểm tra độ sạch, độ khô và tình trạng gỉ sét của bề mặt thép trước khi hàn",
        "Kiểm tra dây hàn, bao bì, dấu oxy hóa và điều kiện bảo quản",
        "Đối chiếu dòng điện, điện áp, tốc độ hàn và tốc độ cấp dây với WPS",
        "Quan sát độ ổn định hồ quang, chiều cao lớp thuốc phủ và bề rộng vũng hàn",
        "Thực hiện VT trong quá trình hàn và UT hoặc RT theo yêu cầu nghiệm thu",
    ),
    measurements=(
        "nhiệt độ và thời gian sấy thuốc hàn theo khuyến cáo của nhà sản xuất",
        "dòng điện, điện áp, tốc độ hàn và tốc độ cấp dây thực tế",
        "độ sạch và độ khô của mép hàn trước khi hàn",
        "chiều cao lớp thuốc phủ trên vùng hồ quang",
        "kết quả UT hoặc RT xác nhận vị trí, kích thước và mật độ lỗ khí",
    ),
    tools=("lò sấy thuốc hàn", "ampe kìm", "đồng hồ đo điện áp", "máy UT", "thiết bị RT", "đèn kiểm tra VT", "weld gauge"),
    repair=(
        "Khoanh vùng lỗ khí theo kết quả VT, UT hoặc RT",
        "Mài hoặc gouging loại bỏ hoàn toàn vùng mối hàn có rỗ khí",
        "Làm sạch lại mép hàn, kiểm tra thuốc hàn và dây hàn trước khi hàn sửa",
        "Hàn sửa đúng WPS với thông số đã được kiểm soát",
        "Kiểm tra lại bằng VT và NDT theo yêu cầu nghiệm thu",
    ),
    verification=(
        "Kết quả UT hoặc RT sau sửa không còn chỉ thị rỗ khí vượt tiêu chí nghiệm thu",
        "Thông số hàn thực tế được ghi nhận và khớp WPS",
        "Thuốc hàn, dây hàn và bề mặt thép được xác nhận sạch, khô và đúng điều kiện sử dụng",
        "Hồ sơ sửa chữa thể hiện vị trí lỗi, nguyên nhân, cách sửa và kết quả kiểm tra lại",
    ),
    prevention=(
        "Bảo quản và sấy thuốc hàn đúng quy trình hoặc khuyến cáo của nhà sản xuất",
        "Làm sạch dầu mỡ, gỉ sét, bụi bẩn và hơi ẩm trên bề mặt thép trước khi hàn",
        "Kiểm tra tình trạng dây hàn trước khi đưa vào sản xuất",
        "Thiết lập, phê duyệt và tuân thủ đúng WPS cho từng loại liên kết",
        "Kiểm soát dòng điện, điện áp, tốc độ hàn và lớp thuốc phủ trong quá trình hàn",
        "Kiểm tra chất lượng trong quá trình sản xuất thay vì chờ đến nghiệm thu cuối",
    ),
    lessons=(
        "Mối hàn đẹp bên ngoài không bảo đảm chất lượng bên trong",
        "Chất lượng hàn SAW phụ thuộc vào vật liệu, thông số, quy trình và kỷ luật kiểm soát",
        "Rỗ khí nhỏ có thể kéo theo sửa chữa lớn nếu phát hiện muộn",
        "Chất lượng không đến từ may mắn mà đến từ quy trình, kỷ luật và trách nhiệm",
    ),
    mistakes=(
        "Dùng thuốc hàn đã hút ẩm nhưng không sấy lại",
        "Bỏ qua dầu mỡ hoặc gỉ sét trên mép hàn vì nhìn bề mặt không nghiêm trọng",
        "Chỉ kiểm tra ngoại quan mà không xem xét UT hoặc RT khi yêu cầu nghiệm thu",
        "Điều chỉnh thông số theo kinh nghiệm nhưng không đối chiếu WPS",
    ),
    standards=("WPS/PQR", "AWS D1.1", "ITP dự án", "tiêu chí UT/RT được phê duyệt"),
)

CRANE_BRAKE = OfflineEngineeringProfile(
    aliases=("cau truc 20 tan bo phanh tang cap khong hoat dong", "crane brake failure", "phanh cau truc", "phanh tang cap"),
    title="Cẩu trục 20 tấn, bộ phanh tang cáp không hoạt động",
    domain="Bảo trì thiết bị nâng",
    problem="Bộ phanh tang cáp không giữ tải làm cẩu trục mất khả năng dừng và giữ vị trí an toàn khi nâng hạ.",
    equipment=("cẩu trục 20 tấn", "bộ phanh tang cáp", "motor nâng", "hộp giảm tốc"),
    component=("má phanh", "tang phanh", "cuộn hút phanh", "lò xo phanh", "cáp tải"),
    symptoms=("phanh không nhả hoặc không đóng đúng lúc", "tải bị trôi khi dừng nâng", "má phanh nóng hoặc mòn không đều", "có tiếng va đập ở cụm phanh", "cẩu phải dừng chờ bảo trì"),
    working_principle="Phanh tang cáp phải đóng đủ lực khi ngắt lệnh và nhả đúng khi motor nâng hoạt động; mọi sai lệch ở má phanh, cuộn hút, lò xo hoặc nguồn điều khiển đều làm giảm khả năng giữ tải.",
    mechanisms=("má phanh mòn làm giảm ma sát giữ tải", "cuộn hút yếu làm phanh nhả không hết", "lò xo phanh mất lực làm phanh đóng không đủ", "tang phanh bẩn hoặc bóng làm hệ số ma sát giảm"),
    causes=("má phanh mòn quá giới hạn hoặc nhiễm dầu mỡ", "khe hở phanh chỉnh sai", "cuộn hút phanh yếu hoặc nguồn cấp không ổn định", "lò xo phanh mỏi, gãy hoặc chỉnh lực sai", "tang phanh mòn, xước hoặc quá nhiệt"),
    consequences=("nguy cơ trôi tải khi dừng nâng", "mất an toàn nghiêm trọng cho người và thiết bị", "hư hỏng cáp, tang, hộp giảm tốc hoặc motor", "dừng sản xuất, tăng chi phí sửa chữa và kiểm định lại"),
    inspection=("cô lập thiết bị và treo cảnh báo không vận hành", "kiểm má phanh, tang phanh và khe hở phanh", "đo nguồn cấp và kiểm cuộn hút phanh", "kiểm lò xo, chốt, cơ cấu tay đòn và điểm kẹt", "thử phanh không tải rồi có tải theo quy trình an toàn", "ghi kết quả vào hồ sơ bảo trì thiết bị nâng"),
    measurements=("khe hở má phanh", "độ mòn má phanh", "điện áp cấp cuộn hút", "nhiệt độ tang phanh", "quãng trôi tải khi dừng"),
    tools=("đồng hồ đo điện", "thước lá", "thước cặp", "camera nhiệt", "phiếu kiểm cẩu trục"),
    repair=("thay má phanh mòn hoặc nhiễm dầu", "chỉnh khe hở và lực lò xo đúng tiêu chí", "sửa nguồn cấp hoặc thay cuộn hút lỗi", "làm sạch hoặc xử lý tang phanh", "thử tải và xác nhận phanh giữ tải ổn định"),
    verification=("phanh đóng nhả dứt khoát", "không còn trôi tải trong điều kiện thử", "nhiệt và tiếng ồn cụm phanh ổn định", "hồ sơ thử phanh được người phụ trách xác nhận"),
    prevention=("kiểm phanh theo lịch trước ca", "đo và ghi khe hở phanh định kỳ", "không vận hành khi có dấu hiệu trôi tải", "vệ sinh cụm phanh tránh dầu mỡ", "đào tạo người vận hành nhận biết dấu hiệu phanh yếu"),
    lessons=("phanh cẩu trục là điểm an toàn sống còn", "không thử may với tải treo", "một khe hở sai có thể tạo rủi ro lớn", "kiểm tra phòng ngừa rẻ hơn sự cố nâng hạ"),
    mistakes=("chỉ chỉnh điện mà không kiểm má phanh", "thử tải khi chưa cô lập khu vực", "bỏ qua dấu hiệu trôi tải nhỏ", "không ghi lịch sử điều chỉnh phanh"),
    standards=("quy trình kiểm định thiết bị nâng", "hướng dẫn OEM", "checklist bảo trì cẩu trục"),
)

PAINT_REWORK = OfflineEngineeringProfile(
    aliases=("san pham phai sua lai sau cong doan da son hoan thien", "painting defect", "sua lai sau son", "coating rework"),
    title="Sản phẩm phải sửa lại sau công đoạn đã sơn hoàn thiện",
    domain="Sơn phủ kết cấu thép",
    problem="Sửa lại sau khi sơn hoàn thiện làm phá vỡ lớp phủ, gây phát sinh làm sạch, dặm sơn, kiểm tra lại và chậm giao hàng.",
    equipment=("cấu kiện thép đã sơn", "khu vực sơn hoàn thiện", "bề mặt phủ", "vùng sửa cơ khí"),
    component=("lớp sơn hoàn thiện", "mép hàn", "lỗ khoan", "bề mặt thép", "vùng dặm sơn"),
    symptoms=("phát hiện sai kích thước hoặc lỗi hàn sau khi đã sơn", "phải mài, khoan hoặc hàn lại trên bề mặt đã phủ", "lớp sơn bong tróc quanh vùng sửa", "màu dặm sơn lệch hoặc DFT không đều", "tiến độ đóng gói bị giữ lại"),
    working_principle="Sơn hoàn thiện là công đoạn bảo vệ cuối; mọi sửa chữa cơ khí sau sơn đều phá màng phủ và buộc quy trình xử lý bề mặt, dặm sơn, đo DFT và nghiệm thu phải lặp lại.",
    mechanisms=("hold point trước sơn không hiệu quả", "lỗi hàn hoặc kích thước lọt qua công đoạn trước", "dữ liệu nghiệm thu chưa khóa trước khi chuyển sơn", "sửa cơ khí tạo cạnh sắc, nhiệt và vùng mất bám dính"),
    causes=("chưa nghiệm thu kích thước, hàn và lỗ trước khi sơn", "checklist trước sơn quá chung", "thiếu phối hợp giữa kiểm soát chất lượng, sản xuất và sơn", "áp lực tiến độ đẩy cấu kiện sang sơn quá sớm", "không khóa NCR trước công đoạn phủ"),
    consequences=("phải xử lý lại bề mặt và dặm sơn", "DFT, màu sắc hoặc độ bám dính không đồng đều", "tăng vật tư, nhân công và thời gian chờ khô", "chậm đóng gói, giao hàng và nghiệm thu khách hàng"),
    inspection=("xác nhận hold point trước sơn", "kiểm kích thước, mối hàn, lỗ và bavia trước chuyển công đoạn", "kiểm NCR còn mở trước khi sơn", "đánh dấu vùng sửa và phạm vi phá lớp phủ", "đo DFT và kiểm ngoại quan sau dặm sơn", "lưu ảnh trước và sau sửa"),
    measurements=("DFT vùng dặm sơn", "độ nhám sau xử lý lại", "kích thước sau sửa", "thời gian khô giữa các lớp", "diện tích lớp phủ bị ảnh hưởng"),
    tools=("máy đo DFT", "weld gauge", "thước đo kích thước", "bộ kiểm độ nhám", "checklist hold point"),
    repair=("khoanh vùng lớp phủ bị ảnh hưởng", "mài sửa hoặc gia công lại đúng bản vẽ", "xử lý bề mặt lại theo yêu cầu sơn", "dặm sơn đúng hệ sơn và thời gian khô", "đo DFT và nghiệm thu lại vùng sửa"),
    verification=("kích thước và lỗi cơ khí đã đạt", "DFT vùng dặm đạt tiêu chí", "màu sắc và ngoại quan đồng nhất", "hồ sơ hold point được cập nhật"),
    prevention=("khóa checklist trước sơn", "không chuyển cấu kiện còn NCR sang sơn", "tổ chức điểm dừng kiểm soát trước phủ", "đào tạo sản xuất nhận biết lỗi phải xử lý trước sơn", "theo dõi chi phí sửa sau sơn để cải tiến"),
    lessons=("sơn hoàn thiện không che được lỗi công đoạn trước", "sửa sau sơn luôn đắt hơn sửa trước sơn", "hold point tốt bảo vệ tiến độ giao hàng", "chất lượng công đoạn trước quyết định chất lượng lớp phủ"),
    mistakes=("đẩy hàng sang sơn khi chưa đủ nghiệm thu", "dặm sơn mà không xử lý bề mặt đúng", "không đo lại DFT vùng sửa", "không phân tích nguyên nhân lọt lỗi"),
    standards=("ITP dự án", "quy trình sơn", "tiêu chí DFT", "NCR nội bộ"),
)

BEARING_NOISE = OfflineEngineeringProfile(
    aliases=("vong bi dong co bi keu", "bearing overheating", "bearing noise", "vong bi qua nhiet", "vong bi bi keu"),
    title="Vòng bi động cơ bị kêu",
    domain="Bảo trì động cơ điện",
    problem="Vòng bi động cơ phát tiếng kêu là dấu hiệu ma sát, mòn, lệch tâm hoặc bôi trơn không ổn định trong cụm quay.",
    equipment=("động cơ điện", "cụm vòng bi", "gối đỡ", "khớp nối"),
    component=("vòng bi", "trục động cơ", "mỡ bôi trơn", "phớt chắn bụi", "gối đỡ"),
    symptoms=("tiếng kêu tăng theo tốc độ quay", "nhiệt độ gối đỡ tăng", "rung tại thân động cơ", "mỡ bôi trơn biến màu hoặc rò rỉ", "dòng tải dao động khi máy chạy"),
    working_principle="Vòng bi phải giữ trục quay ổn định với ma sát thấp; thiếu bôi trơn, nhiễm bẩn, lệch tâm hoặc tải bất thường làm tăng nhiệt, rung và tiếng ồn.",
    mechanisms=("màng bôi trơn suy giảm làm kim loại tiếp xúc trực tiếp", "bụi hoặc nước vào vòng bi làm hỏng bề mặt lăn", "lệch tâm khớp nối tạo tải hướng kính", "quá tải hoặc lắp sai làm vòng bi mòn sớm"),
    causes=("thiếu mỡ hoặc dùng sai loại mỡ bôi trơn", "vòng bi nhiễm bụi, nước hoặc tạp chất", "khớp nối hoặc trục bị lệch tâm", "vòng bi lắp sai hoặc quá chặt", "động cơ vận hành quá tải hoặc thông gió kém"),
    consequences=("hư hỏng vòng bi và trục động cơ", "tăng nhiệt gây hỏng cuộn dây hoặc phớt", "dừng máy đột xuất", "tăng chi phí thay thế và mất sản lượng"),
    inspection=("nghe tiếng kêu theo tốc độ và tải", "đo rung tại các điểm gối đỡ", "đo nhiệt độ vòng bi", "kiểm tình trạng mỡ và phớt", "kiểm đồng tâm khớp nối", "đối chiếu lịch bôi trơn và thay vòng bi"),
    measurements=("nhiệt độ gối đỡ", "mức rung", "dòng điện động cơ", "độ lệch tâm khớp nối", "thời gian chạy từ lần bôi trơn gần nhất"),
    tools=("camera nhiệt", "máy đo rung", "ống nghe cơ khí", "ampe kìm", "đồng hồ so"),
    repair=("bổ sung hoặc thay đúng loại mỡ", "thay vòng bi khi có dấu mòn hoặc rỗ", "căn chỉnh khớp nối", "kiểm và thay phớt chắn bụi", "chạy thử và đo lại nhiệt rung"),
    verification=("tiếng kêu giảm rõ sau sửa", "nhiệt độ và rung ổn định", "dòng tải không dao động bất thường", "lịch bôi trơn được cập nhật"),
    prevention=("lập lịch bôi trơn theo điều kiện vận hành", "kiểm rung và nhiệt định kỳ", "giữ khu vực động cơ sạch và khô", "căn chỉnh khớp nối sau bảo trì", "thay vòng bi theo tình trạng thay vì chờ hỏng"),
    lessons=("tiếng kêu nhỏ là cảnh báo sớm", "vòng bi hỏng có thể kéo theo hỏng động cơ", "đo rung và nhiệt giúp tránh thay mò", "bôi trơn đúng là bảo trì rẻ nhất"),
    mistakes=("bơm quá nhiều mỡ", "thay vòng bi nhưng không căn chỉnh", "bỏ qua nhiễm bẩn", "chạy tiếp khi vòng bi đã nóng và kêu"),
    standards=("hướng dẫn OEM", "kế hoạch PM", "tiêu chí rung nội bộ"),
)

PROFILES = (SAW_POROSITY, CRANE_BRAKE, PAINT_REWORK, BEARING_NOISE)


def build_offline_engineering_record(topic_intent: TopicIntent) -> EngineeringRecord | None:
    normalized = _normalize(topic_intent.original_topic)
    profile = next(
        (
            item
            for item in PROFILES
            if any(_contains(normalized, alias) for alias in item.aliases)
        ),
        None,
    )
    if profile is None:
        return None
    return EngineeringRecord(
        topic=profile.title if profile is SAW_POROSITY else topic_intent.original_topic,
        domain=profile.domain,
        primary_domain=topic_intent.primary_domain,
        secondary_domain=topic_intent.secondary_domain,
        topic_type=topic_intent.topic_type,
        main_entity=profile.equipment[0],
        observed_condition=profile.symptoms[0],
        expected_user_goal=topic_intent.expected_user_goal,
        safety_level=topic_intent.safety_level,
        request_id=topic_intent.request_id,
        topic_fingerprint=topic_intent.topic_fingerprint,
        title=profile.title,
        problem=profile.problem,
        equipment=profile.equipment,
        subsystem=profile.domain,
        component=profile.component,
        failure_symptom=profile.symptoms,
        operating_context=f"Chủ đề được xử lý theo kinh nghiệm hiện trường trong {profile.domain}.",
        working_principle=profile.working_principle,
        failure_mechanisms=profile.mechanisms,
        root_causes=profile.causes,
        evidence_required=("ảnh hiện trường", "kết quả kiểm tra", "hồ sơ công đoạn liên quan"),
        inspection_procedure=profile.inspection,
        measurements=profile.measurements,
        tools_required=profile.tools,
        decision_logic=(
            "Xử lý theo nguyên nhân đã xác nhận, không chỉ theo dấu hiệu nhìn thấy.",
            "Chỉ bàn giao khi kết quả kiểm tra lại phù hợp tiêu chí nghiệm thu.",
            "Nếu lỗi lặp lại, mở NCR hoặc phiếu cải tiến để khóa nguyên nhân hệ thống.",
        ),
        repair_procedure=profile.repair,
        verification=profile.verification,
        acceptance_criteria=profile.consequences,
        lessons_learned=profile.lessons,
        common_mistakes=profile.mistakes,
        preventive_maintenance=profile.prevention,
        safety_controls=("dùng PPE phù hợp", "kiểm soát khu vực thao tác", "chỉ cho người có thẩm quyền thực hiện kiểm tra"),
        kaizen=("chuẩn hóa điểm kiểm trước công đoạn", "ghi nhận lỗi lặp lại theo ca", "đưa bài học vào checklist"),
        digital_factory_recommendations=("lưu ảnh và kết quả kiểm tra theo mã cấu kiện hoặc mã thiết bị",),
        applicable_standards=profile.standards,
        confidence=0.86,
        source_keys=("OFFLINE_ENGINEERING_PROFILE",),
    )


def _contains(normalized: str, alias: str) -> bool:
    normalized_alias = _normalize(alias)
    return bool(normalized_alias and normalized_alias in normalized)


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", (value or "").lower())
    no_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    no_marks = no_marks.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", no_marks).strip()
