---
name: docx-to-markdown-py
description: Convert an attached .docx file to markdown text (Python, server-side).
version: 1
---

# docx-to-markdown-py

Converts a `.docx` file to plain Markdown text. The conversion runs server-side
in the AO sandbox using only Python stdlib — no network access, no pip installs.

## When to use

Load this skill when the user attaches or references a `.docx` file and wants its
content extracted as Markdown (for editing, summarising, or importing into DA).

## How to run

1. Obtain the file bytes as base64. If the user uploaded a file, read it from
   `${AGENT_UPLOADS_ROOT}/<filename>` and base64-encode it:

```python
import base64, json, subprocess, sys

with open("${AGENT_UPLOADS_ROOT}/<filename>", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({"bytesBase64": b64})

result = subprocess.run(
    ["python3", "${AGENT_SKILL_DIR}/scripts/convert.py"],
    input=payload,
    capture_output=True,
    text=True,
    timeout=30,
)
output = json.loads(result.stdout)
print(output.get("markdown") or output.get("error"))
```

2. The script writes `{"markdown": "<text>"}` to stdout on success,
   or `{"error": "<message>"}` on failure.

## Output

Return the extracted markdown to the user. If the user wants to create a DA page
from it, delegate to the DA Content Agent via `agent_task`.

## Notes

- Plain text only — bold, italic, and tables are not preserved in this version.
- Extracts `word/document.xml`, `word/header1.xml`, and `word/footer1.xml`.
- XML entities (`&amp;`, `&lt;`, etc.) are handled by the stdlib XML parser.
