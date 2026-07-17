# PROMPT_REWRITE_REPORT.md

## Scope

Repository: `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

Modified production surface:

- `src/hgpt_ai_os/engineering_pipeline/pipeline.py`

Focused verification fixture:

- `tests/test_engineering_pipeline_v2.py`

Unchanged by this patch:

- GUI
- Provider
- ConfigManager
- ProviderManager
- Runtime
- DOCX Exporter
- Packaging
- Installers
- Engineering renderers

## New Engineering Prompt

### System role

```text
You are the Chief Mechanical Engineer of HGPT Steel.

Experience base:
- Steel structures
- Mechanical design
- Maintenance
- Hydraulics
- Pneumatics
- Electrical
- PLC
- Automation
- QA/QC
- Welding
- Root Cause Analysis
- Reliability Engineering
- Lean
- TPM
- Kaizen

Never answer like ChatGPT.
Answer like an engineering expert writing an internal technical report for HGPT Steel.
Return only one EngineeringRecord JSON object. Do not generate Facebook, SEO, checklist,
TikTok, image prompt, video prompt, hashtags, marketing copy, or management filler.
```

### EngineeringRecord task prompt

```text
Given exactly one engineering topic, generate exactly one EngineeringRecord.

The EngineeringRecord must contain all required engineering sections:
- title
- equipment
- subsystem
- component
- working_principle
- failure_symptom
- root_causes
- inspection_procedure
- measurements
- tools_required
- decision_logic
- repair_procedure
- verification
- acceptance_criteria
- common_mistakes
- safety_controls
- preventive_maintenance
- lessons_learned
- kaizen
- digital_factory_recommendations
- applicable_standards
- confidence
- missing_information

Root cause requirements:
- Provide at least 3 root causes.
- Rank causes by probability.
- Each root_causes item must be a complete cause block, not a short label.
- For every cause include: probability rank, why it happens, physical mechanism,
  inspection method, measurement, required tools, expected values if known, decision
  logic, repair procedure, verification after repair, and acceptance criteria.
- If a measurement value or expected value is unknown, do not invent a number.
  Write exactly: "Không đủ dữ liệu để kết luận. Cần đo..." and state the exact
  measurement required.

Quality requirements:
- Do not fabricate standards.
- Do not fabricate measurements.
- Do not fabricate numbers.
- Do not write generic management paragraphs.
- Do not repeat the same text across unrelated topics.
- Make the answer topic-specific. A motor bearing noise record, a three-phase
  motor overheating record, a hydraulic pump low-pressure record, a VFD OC record,
  and a PLC-HMI communication loss record must have substantially different
  causes, inspections, tools, repair actions, verification, lessons, PM, Kaizen,
  and Digital Factory recommendations.

Internal rejection rule:
Reject your own draft and rewrite before returning if root_causes has fewer than
3 items, inspection is missing, repair is missing, verification is missing,
lessons_learned is missing, or preventive_maintenance is missing.
```

## EngineeringRecord Schema

The prompt now sends a stricter JSON schema through `EngineeringGenerationPipeline.RECORD_SCHEMA`.

Required shape:

- `title`: string
- `topic`: string
- `problem`: string
- `domain`: string
- `equipment`: array of strings identifying the asset class
- `subsystem`: string
- `component`: array of affected components
- `failure_symptom`: array of topic-specific observed symptoms
- `operating_context`: string
- `working_principle`: string
- `failure_mechanisms`: array of strings
- `root_causes`: array of at least 3 ranked cause blocks
- `evidence_required`: array of evidence needed before conclusion
- `inspection_procedure`: array of inspection steps
- `measurements`: array of exact measurements required, without fabricated values
- `tools_required`: array of instruments and tools
- `decision_logic`: array of if/then diagnostic logic
- `repair_procedure`: array of repair steps
- `verification`: array of post-repair verification steps
- `acceptance_criteria`: array of pass/fail criteria without invented values
- `common_mistakes`: array of topic-specific mistakes
- `safety_controls`: array of safety controls
- `preventive_maintenance`: array of PM actions
- `lessons_learned`: array of technical lessons
- `kaizen`: array of improvement ideas
- `digital_factory_recommendations`: array of data/logging/trending recommendations
- `applicable_standards`: array only when standards are truly known
- `missing_information`: array using `Không đủ dữ liệu để kết luận. Cần đo...` when input is insufficient
- `confidence`: numeric `0.0` to `1.0`
- `source_keys`: array, expected to include `AI_PROVIDER`

The pipeline now rejects AI JSON before rendering when `root_causes` has fewer than 3 valid items.

## Example AI Response For Five Topics

The examples below are the EngineeringRecord reasoning patterns verified through generated DOCX files. They are intentionally different by failure physics, tools, measurements, repair logic, and digital recommendations.

### 1. Vòng bi động cơ bị kêu

Representative root causes:

- Hạng 1: bôi trơn sai hoặc mỡ suy giảm. Mechanism: mất màng bôi trơn, kim loại tiếp xúc kim loại, nhiệt và rung tăng. Tools: camera nhiệt, vibration meter, ống nghe cơ khí, súng bơm mỡ đã hiệu chuẩn.
- Hạng 2: lệch tâm khớp nối hoặc mềm chân đế. Mechanism: tải hướng kính tuần hoàn ép bi vào rãnh lăn. Tools: đồng hồ so hoặc cân laser, thước lá, cờ lê lực.
- Hạng 3: vòng bi mỏi, rỗ hoặc lắp sai dung sai. Mechanism: rãnh lăn bong tróc tạo xung va đập. Tools: vibration analyzer, đồng hồ so, cảo chuyên dụng, gia nhiệt vòng bi.

Missing data wording:

```text
Không đủ dữ liệu để kết luận. Cần đo rung, nhiệt gối đỡ, đồng tâm khớp nối và tình trạng mỡ trước khi kết luận.
```

### 2. Động cơ 3 pha bị nóng

Representative root causes:

- Hạng 1: quá tải cơ hoặc kẹt cơ cấu kéo. Mechanism: dòng stator tăng, tổn hao I2R tăng, nhiệt cuộn dây tăng. Tools: ampe kìm true RMS, tachometer, camera nhiệt.
- Hạng 2: mất cân bằng điện áp hoặc tiếp xúc nguồn kém. Mechanism: lệch áp tạo lệch dòng, một pha nóng hơn. Tools: đồng hồ true RMS, ampe kìm, camera nhiệt.
- Hạng 3: làm mát kém hoặc môi trường quá nóng/bụi. Mechanism: nhiệt sinh ra không thoát được. Tools: camera nhiệt, nhiệt kế, anemometer nếu có.

Missing data wording:

```text
Không đủ dữ liệu để kết luận. Cần đo dòng từng pha, điện áp pha-pha, nhiệt vỏ motor, tải cơ và tình trạng làm mát.
```

### 3. Bơm thủy lực bị mất áp

Representative root causes:

- Hạng 1: hút khí hoặc cavitation đường hút. Mechanism: bọt khí xẹp làm xói mòn và giảm lưu lượng hiệu dụng. Tools: đồng hồ áp/chân không thủy lực, kính quan sát dầu, bộ lấy mẫu dầu.
- Hạng 2: van relief kẹt mở hoặc chỉnh sai. Mechanism: lưu lượng bơm xả về thùng trước khi tạo áp cho tải. Tools: đồng hồ áp thủy lực, sơ đồ mạch, thiết bị khóa chỉnh.
- Hạng 3: mòn bơm hoặc rò rỉ nội trong cơ cấu chấp hành. Mechanism: lưu lượng hồi nội tăng, áp không giữ khi có tải. Tools: flow meter, đồng hồ áp, camera nhiệt, kit lấy mẫu dầu.

Missing data wording:

```text
Không đủ dữ liệu để kết luận. Cần đo áp bơm, lưu lượng, nhiệt dầu, chênh áp lọc và trạng thái relief.
```

### 4. Biến tần báo OC

Representative root causes:

- Hạng 1: tải cơ kẹt hoặc mô men khởi động quá cao. Mechanism: motor cần mô men lớn, VFD cấp dòng cao và trip OC. Tools: keypad VFD/log lỗi, ampe kìm true RMS phù hợp VFD.
- Hạng 2: ramp tăng tốc hoặc tham số motor sai. Mechanism: drive đòi dòng từ hóa/mô men quá lớn trong thời gian ngắn. Tools: keypad/software VFD, nameplate motor, laptop.
- Hạng 3: cáp/motor chạm đất hoặc suy cách điện. Mechanism: dòng rò/chập cục bộ làm dòng VFD tăng đột ngột. Tools: megger phù hợp, đồng hồ, sơ đồ đấu dây.

Missing data wording:

```text
Không đủ dữ liệu để kết luận. Cần đọc fault log VFD, dòng lúc trip, ramp/parameter và đo cách điện motor/cáp.
```

### 5. PLC mất kết nối HMI

Representative root causes:

- Hạng 1: lỗi vật lý mạng hoặc nguồn 24VDC không ổn định. Mechanism: link layer mất carrier hoặc thiết bị reboot. Tools: đồng hồ, cable tester, laptop ping.
- Hạng 2: sai địa chỉ, driver hoặc cấu hình truyền thông. Mechanism: thiết bị online nhưng HMI không ánh xạ đúng endpoint/tag. Tools: engineering software, bản backup chuẩn, network scanner.
- Hạng 3: nhiễu EMC hoặc quá tải truyền thông. Mechanism: lỗi frame hoặc CPU/network quá tải làm timeout. Tools: managed switch log, phần mềm PLC, kiểm tra tiếp địa.

Missing data wording:

```text
Không đủ dữ liệu để kết luận. Cần đo nguồn 24VDC, kiểm link mạng, log ping, đọc IP/driver/project version.
```

## Runtime Verification

Focused test command:

```bash
PYTHONPYCACHEPREFIX=/tmp/lucid_pycache PYTHONPATH=src python3 -m unittest tests.test_engineering_pipeline_v2
```

Result:

```text
Ran 3 tests in 2.013s
OK
```

Runtime evidence:

- The focused test asserts the system prompt contains `Chief Mechanical Engineer of HGPT Steel`.
- The focused test asserts the user prompt contains `Root causes must have at least 3 items`.
- The focused test asserts the user prompt contains `Không đủ dữ liệu để kết luận. Cần đo...`.
- The pipeline accepts AI records only after required fields exist and `root_causes` contains at least 3 valid items.
- The unchanged renderer produced 7 document payloads per EngineeringRecord.
- The unchanged DOCX exporter produced 35 DOCX files for the 5 test topics.

Generated DOCX evidence root:

```text
work/prompt_rewrite_evidence
```

Generated evidence files:

```text
work/prompt_rewrite_evidence/01_Vòng_bi_động_cơ_bị_kêu/facebook.docx
work/prompt_rewrite_evidence/02_Động_cơ_3_pha_bị_nóng/facebook.docx
work/prompt_rewrite_evidence/03_Bơm_thủy_lực_bị_mất_áp/facebook.docx
work/prompt_rewrite_evidence/04_Biến_tần_báo_OC/facebook.docx
work/prompt_rewrite_evidence/05_PLC_mất_kết_nối_HMI/facebook.docx
```

DOCX count:

```text
35
```

## Extracted DOCX Evidence

### Vòng bi động cơ bị kêu

Extracted from `work/prompt_rewrite_evidence/01_Vòng_bi_động_cơ_bị_kêu/facebook.docx`:

```text
Dấu hiệu cần xác nhận
tiếng rít hoặc lạo xạo theo tốc độ quay
rung tăng tại thân motor
nhiệt gối đỡ có xu hướng tăng
Nguyên nhân gốc cần khoanh vùng
Hạng 1 - bôi trơn sai hoặc mỡ suy giảm. Vì sao xảy ra: thiếu mỡ, thừa mỡ, sai chủng loại hoặc nhiễm bụi làm vòng bi chạy khô cục bộ. Cơ chế vật lý: màng bôi trơn mất ổn định, kim loại tiếp xúc kim loại, nhiệt và rung tăng. Kiểm tra: nghe bằng ống nghe cơ khí, kiểm tra màu mỡ, dấu chảy mỡ, lịch sử tra mỡ. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo nhiệt độ gối đỡ, phổ rung và tình trạng mỡ. Dụng cụ: camera nhiệt, vibration meter, ống nghe cơ khí, súng bơm mỡ đã hiệu chuẩn.
```

### Động cơ 3 pha bị nóng

Extracted from `work/prompt_rewrite_evidence/02_Động_cơ_3_pha_bị_nóng/facebook.docx`:

```text
Dấu hiệu cần xác nhận
vỏ motor nóng bất thường
mùi cách điện nóng
dòng chạy cao hoặc lệch pha
relay nhiệt có thể tác động
Nguyên nhân gốc cần khoanh vùng
Hạng 1 - quá tải cơ hoặc kẹt cơ cấu kéo. Vì sao xảy ra: tải vượt khả năng motor, bạc đạn tải kẹt, truyền động căng hoặc vật liệu kẹt. Cơ chế vật lý: dòng stator tăng, tổn hao I2R tăng và nhiệt cuộn dây tăng. Kiểm tra: tách tải nếu an toàn, kiểm tra truyền động, nghe tiếng tải, xem dòng theo từng pha. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo dòng từng pha khi chạy tải thực tế và so với nameplate/OEM.
```

### Bơm thủy lực bị mất áp

Extracted from `work/prompt_rewrite_evidence/03_Bơm_thủy_lực_bị_mất_áp/facebook.docx`:

```text
Dấu hiệu cần xác nhận
áp suất không lên
xy lanh yếu hoặc không giữ tải
bơm kêu cavitation
dầu nóng nhanh
Nguyên nhân gốc cần khoanh vùng
Hạng 1 - hút khí hoặc cavitation đường hút. Vì sao xảy ra: mức dầu thấp, lọc hút nghẹt, ống hút hở hoặc dầu quá đặc. Cơ chế vật lý: vùng hút áp thấp tạo bọt khí, bọt xẹp làm xói mòn và giảm lưu lượng hiệu dụng. Kiểm tra: kiểm tra mức dầu, bọt trong thùng, tiếng kêu bơm, lọc hút và kẹp ống. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo chân không đường hút hoặc chênh áp lọc nếu hệ thống có điểm đo.
```

### Biến tần báo OC

Extracted from `work/prompt_rewrite_evidence/04_Biến_tần_báo_OC/facebook.docx`:

```text
Dấu hiệu cần xác nhận
VFD trip OC khi khởi động hoặc tăng tốc
motor giật hoặc không đạt tốc độ
lỗi lặp lại theo tải hoặc theo ramp
Nguyên nhân gốc cần khoanh vùng
Hạng 1 - tải cơ kẹt hoặc mô men khởi động quá cao. Vì sao xảy ra: cơ cấu tải bị kẹt, bạc đạn tải hỏng, băng tải đầy tải hoặc cơ cấu nâng giữ tải. Cơ chế vật lý: motor cần mô men lớn, VFD cấp dòng cao và trip OC. Kiểm tra: tách tải nếu an toàn, quay tay cơ cấu, xem lỗi xuất hiện lúc start hay tăng tốc. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo dòng motor tại thời điểm trip và trạng thái tải.
```

### PLC mất kết nối HMI

Extracted from `work/prompt_rewrite_evidence/05_PLC_mất_kết_nối_HMI/facebook.docx`:

```text
Dấu hiệu cần xác nhận
HMI báo communication error
không đọc/ghi được tag
PLC vẫn chạy nhưng màn hình treo dữ liệu
mất kết nối theo chu kỳ hoặc sau mất điện
Nguyên nhân gốc cần khoanh vùng
Hạng 1 - lỗi vật lý mạng hoặc nguồn 24VDC không ổn định. Vì sao xảy ra: đầu RJ45 lỏng, cáp gãy, switch công nghiệp mất nguồn, nguồn 24VDC sụt khi tải đóng cắt. Cơ chế vật lý: link layer mất carrier hoặc thiết bị reboot, HMI mất phiên truyền thông. Kiểm tra: đèn link/activity, nguồn PLC/HMI/switch, đầu cáp, log reboot. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo 24VDC tại terminal khi máy chạy và test cáp mạng.
```

## Conclusion

The prompt rewrite is applied at the real AI EngineeringGenerationPipeline entrypoint. The renderer and DOCX exporter remain unchanged. Generated DOCX evidence demonstrates clearly different engineering reasoning for all five required topics.
