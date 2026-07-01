"""
Convert a .docx file to plain Markdown text.

Reads base64-encoded .docx bytes from stdin as JSON:
  {"bytesBase64": "<base64>"}

Writes JSON to stdout:
  {"markdown": "<text>"}   on success
  {"error": "<message>"}   on failure

Uses only stdlib — no pip installs required.
"""

import base64
import json
import sys
import zipfile
import io
import xml.etree.ElementTree as ET

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def _extract_text(xml_bytes: bytes) -> str:
    """Extract paragraph text from a Word XML part."""
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for para in root.iter(f"{{{NS}}}p"):
        runs = "".join(
            node.text or ""
            for node in para.iter(f"{{{NS}}}t")
        )
        if runs.strip():
            paragraphs.append(runs)
    return "\n\n".join(paragraphs)

def convert(bytes_base64: str) -> str:
    raw = base64.b64decode(bytes_base64)
    buf = io.BytesIO(raw)
    parts = []
    with zipfile.ZipFile(buf) as zf:
        names = zf.namelist()
        for target in ("word/document.xml", "word/header1.xml", "word/footer1.xml"):
            if target in names:
                parts.append(_extract_text(zf.read(target)))
    return "\n\n".join(p for p in parts if p)

def main():
    payload = json.load(sys.stdin)
    bytes_b64 = payload.get("bytesBase64", "")
    if not bytes_b64:
        print(json.dumps({"error": "bytesBase64 is required"}))
        sys.exit(0)
    markdown = convert(bytes_b64)
    print(json.dumps({"markdown": markdown}))

main()
