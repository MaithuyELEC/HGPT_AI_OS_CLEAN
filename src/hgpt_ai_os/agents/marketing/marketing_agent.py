from pathlib import Path
from datetime import datetime


class MarketingAgent:

    def create_day11_content(self):
        base_dir = Path("outputs/marketing/day11")
        base_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")

        files = {
            "facebook.md": f"""# Day 11 - Facebook Post

Date: {today}

Chủ đề: HGPT_AI_OS đã boot thành công Core v0.1

Nội dung:
Hôm nay HGPT chính thức hoàn thành bước đầu tiên của hành trình xây dựng hệ điều hành AI nội bộ: HGPT_AI_OS Core v0.1.

Hệ thống đã chạy được:
- CLI
- Runtime
- Kernel
- Agent
- Task Create / List / Run / Complete
- Smoke Test PASS

Đây không chỉ là vài dòng code. Đây là nền móng để HGPT từng bước tự động hóa quản lý, sản xuất, bảo trì, dự án, QA/QC và marketing.

Mỗi ngày một bước nhỏ.
Mỗi bước nhỏ tạo thành một nhà máy số.

#HGPT #HGPTSteel #AIOS #DigitalFactory #Automation #SteelStructure
""",

            "tiktok.md": f"""# Day 11 - TikTok Script

Hook:
Chúng tôi vừa boot thành công hệ điều hành AI đầu tiên cho nhà máy cơ khí kết cấu thép.

Body:
Đây là HGPT_AI_OS Core v0.1.
Nó có thể chạy lệnh, tạo task, lưu task, chạy task và hoàn tất task.

Điều này mở đường cho việc tự động hóa:
- Bảo trì
- QA/QC
- Quản lý dự án
- Sản xuất
- Marketing

CTA:
Theo dõi hành trình xây dựng HGPT Steel Digital Factory mỗi ngày.

Hashtag:
#HGPT #AIOS #DigitalFactory #SteelFactory #Automation
""",

            "image_prompt.md": """# Image Prompt

A futuristic steel structure factory control room, digital dashboard, AI operating system interface, industrial steel fabrication environment, engineers monitoring automation workflows, clean modern lighting, professional corporate style, HGPT Steel Digital Factory concept.
""",

            "video_prompt.md": """# Video Prompt

Create a 15-second vertical video showing:
1. A steel fabrication factory.
2. A digital AI operating system dashboard booting up.
3. Task flow: Create → Run → Complete.
4. Engineers reviewing automation results.
5. Closing text: "HGPT_AI_OS Core v0.1 - Boot Passed".

Style: modern industrial, professional, cinematic, high-tech factory automation.
""",

            "seo.md": """# SEO

Title:
HGPT_AI_OS Core v0.1 chính thức boot thành công

Meta Description:
HGPT Steel bắt đầu hành trình xây dựng hệ điều hành AI nội bộ phục vụ tự động hóa nhà máy cơ khí kết cấu thép.

Keywords:
HGPT, HGPT Steel, AI OS, Digital Factory, Steel Structure Automation, Nhà máy số, Tự động hóa cơ khí
""",

            "approval_checklist.md": """# Approval Checklist

- [ ] Đọc Facebook post
- [ ] Đọc TikTok script
- [ ] Kiểm tra hashtag
- [ ] Kiểm tra image prompt
- [ ] Kiểm tra video prompt
- [ ] Duyệt đăng Facebook
- [ ] Duyệt đăng TikTok
"""
        }

        for filename, content in files.items():
            (base_dir / filename).write_text(content, encoding="utf-8")

        return base_dir
