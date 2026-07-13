# Chứng nhận bản vá cuối

## Tệp đã sửa

- `src/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json`
- `src/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`
- `src/hgpt_ai_os/topic_engine/writers/checklist_writer.py`
- `tests/test_topic_engine.py`

## Kết quả hồi quy

- `PYTHONPATH=src python3 -m unittest tests.test_topic_engine`: đạt, 29 kiểm thử.
- `PYTHONPATH=src python3 -m unittest discover -s tests`: đạt, 134 kiểm thử.
- `Băng tải buồng phun bi bị lệch`: chọn `CONVEYOR_BELT_MISALIGNMENT`.
- `Cầu trục 7.5T bị đứt cáp`: giữ `WIRE_ROPE_FAILURE`.
- `Máy nén khí áp thấp`: giữ `AIR_COMPRESSOR_LOW_PRESSURE`.
- `Đường hàn SAW bị rỗ khí`: giữ `SAW_POROSITY`.
- `Đường hàn SAW bị cháy cạnh`: giữ `SAW_UNDERCUT`.
- `Bong tróc sơn`: giữ `PAINT_PEELING`.

## Kiểm tra tiếng Việt

- Các nhãn tiếng Anh bắt buộc thay thế đã được quét trong DOCX xuất thật.
- Không còn nhãn tiếng Anh trong danh sách chứng nhận.
- Nhãn danh mục kiểm tra cố định đã đổi thành `Danh mục kiểm tra hiện trường`.

## Kiểm tra điều hướng

- Chủ đề có đồng thời `băng tải` và `lệch` được đưa vào mã kỹ thuật `CONVEYOR_BELT_MISALIGNMENT`.
- Luồng này thắng trước nhóm phun bi và không rơi vào bộ tri thức bánh công tác.
- Không thay đổi kết quả của các chủ đề cầu trục, máy nén khí, hai chủ đề SAW và bong tróc sơn.

## Kiểm tra tri thức

- Bộ tri thức mới có đủ: cơ chế hư hỏng, dấu hiệu nhận biết, nguyên nhân gốc, phương pháp kiểm tra, đo kiểm, quy trình sửa chữa, kiểm tra sau sửa, bảo trì phòng ngừa, bài học kinh nghiệm và đề xuất Digital Factory.
- Tri thức băng tải bao phủ đầy đủ các khái niệm bắt buộc về chạy lệch băng, tang đầu, tang đuôi, con lăn đỡ, con lăn hồi, idler, cụm căng băng, mối nối băng, lực căng băng, căn chỉnh con lăn, căn chỉnh tang, căn laser, bạc đạn, độ đảo trục, căn chỉnh khung, vật liệu bám dính và scraper.
- Nội dung xuất ra tập trung vào căn chỉnh băng tải, tang, con lăn, lực căng, mối nối băng, bạc đạn, độ đảo trục, khung và vật liệu bám dính.

## Kiểm tra DOCX

- Đã chạy `production.build_outputs(914, "Băng tải buồng phun bi bị lệch", open_output_folder=False)`.
- Thư mục kiểm chứng: `/Users/macos/Documents/LUCID/outputs/marketing/Day914`.
- Đã đọc lại text trực tiếp từ `approval_checklist.docx`, `facebook.docx`, `hashtags.docx`, `image_prompt.docx`, `seo.docx`, `tiktok.docx`, `video_prompt.docx`.
- Không phát hiện: `blast wheel`, `impeller`, `control cage`, `separator`, `blade`, `bucket elevator`.
- Không phát hiện nhãn nội bộ bị cấm trong DOCX đã xuất.
- Chủ đề băng tải chỉ dùng tri thức băng tải, không lẫn nội dung bánh công tác phun bi.

READY FOR CODE FREEZE
