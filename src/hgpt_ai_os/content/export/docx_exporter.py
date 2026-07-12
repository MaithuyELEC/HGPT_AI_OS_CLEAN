from pathlib import Path
import re

from docx import Document


class DocxExporter:
    _HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$")
    _BULLET_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
    _BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
    _FORBIDDEN_TEMPLATE_LABEL_RE = re.compile(
        r"(?im)^\s*"
        r"("
        r"Story|Pain|Truth|Hook|Curiosity|Practical actions|"
        r"Scene|Camera|Voice|Caption|Transition|Negative prompt|"
        r"Duration|Aspect ratio|Lens|Lighting|Composition|Mood|Texture|"
        r"Problem|One practical tip|CTA"
        r")\s*:",
    )
    _FORBIDDEN_LEAKAGE_PHRASE_RE = re.compile(
        r"\b("
        r"Manager's job|Quality release|Hold the product|The topic belongs to"
        r")\b",
        re.IGNORECASE,
    )
    _BROKEN_VIETNAMESE_RE = re.compile(
        r"\b("
        r"[Đđ]\s+ng\s+c|"
        r"ki\s+m\s+tra|"
        r"b\s+ng\s+ch\s+ng"
        r")\b",
        re.IGNORECASE,
    )

    def save(self, path: Path, title: str, content: str):

        path.parent.mkdir(parents=True, exist_ok=True)
        self.validate_content(str(content))

        doc = Document()
        self._set_vietnamese_font(doc)
        doc.add_heading(title, level=1)
        self._add_markdown_content(doc, str(content))
        doc.save(path)

    def validate_content(self, content: str) -> None:
        if content.encode("utf-8").decode("utf-8") != content:
            raise ValueError("DOCX export blocked: invalid UTF-8 content.")
        forbidden = self._FORBIDDEN_TEMPLATE_LABEL_RE.search(content)
        if forbidden:
            label = forbidden.group(1)
            raise ValueError(
                f"DOCX export blocked: forbidden English text '{label}'."
            )
        forbidden = self._FORBIDDEN_LEAKAGE_PHRASE_RE.search(content)
        if forbidden:
            raise ValueError(
                f"DOCX export blocked: forbidden English text '{forbidden.group(0)}'."
            )
        broken = self._BROKEN_VIETNAMESE_RE.search(content)
        if broken:
            raise ValueError(
                f"DOCX export blocked: broken Vietnamese text '{broken.group(0)}'."
            )

    def _set_vietnamese_font(self, doc: Document) -> None:
        for style_name in ("Normal", "Heading 1", "Heading 2", "Heading 3"):
            style = doc.styles[style_name]
            style.font.name = "Arial"

    def _add_markdown_content(self, doc: Document, content: str):
        for raw_line in content.splitlines():
            line = raw_line.strip()

            if not line:
                doc.add_paragraph()
                continue

            heading = self._HEADING_RE.match(line)
            if heading:
                level = min(len(heading.group(1)), 3)
                paragraph = doc.add_heading(level=level)
                self._add_inline_markdown(paragraph, heading.group(2).strip())
                continue

            bullet = self._BULLET_RE.match(line)
            if bullet:
                paragraph = doc.add_paragraph(style="List Bullet")
                self._add_inline_markdown(paragraph, bullet.group(1).strip())
                continue

            paragraph = doc.add_paragraph()
            self._add_inline_markdown(paragraph, line)

    def _add_inline_markdown(self, paragraph, text: str):
        position = 0

        for match in self._BOLD_RE.finditer(text):
            if match.start() > position:
                paragraph.add_run(text[position : match.start()])

            run = paragraph.add_run(match.group(1))
            run.bold = True
            position = match.end()

        if position < len(text):
            paragraph.add_run(text[position:])
