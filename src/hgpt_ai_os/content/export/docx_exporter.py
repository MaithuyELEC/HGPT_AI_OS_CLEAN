from pathlib import Path
import re

from docx import Document


class DocxExporter:
    _HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$")
    _BULLET_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
    _BOLD_RE = re.compile(r"\*\*(.+?)\*\*")

    def save(self, path: Path, title: str, content: str):

        path.parent.mkdir(parents=True, exist_ok=True)

        doc = Document()
        doc.add_heading(title, level=1)
        self._add_markdown_content(doc, str(content))
        doc.save(path)

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
