# BPD Generator

A Streamlit + python-docx app for generating Business Process Documents
in a fixed corporate format. Build documents block-by-block in the UI,
then export a polished `.docx` you can hand to anyone.

## Features

- **Block-based authoring** — Heading, Subheading, Normal Heading,
  Paragraph, Image, Table
- **Auto-numbered headings** (`1`, `1.1`, …) with UPPERCASE conversion
  for Heading / Subheading
- **Live Table of Contents** generated as a Word TOC field — refreshes
  inside Word with one click (or on open)
- **Custom Word styles** (`BPD Heading`, `BPD Subheading`, etc.) so
  formatting stays consistent and editable
- **Image blocks** with maintained aspect ratio, centered, page-relative
  width, black border, vertical spacing
- **Table blocks** with bold grey header row, black borders, Calibri 10
- **Header & footer** with placeholder for a logo and an auto page
  number
- **Reorder & delete** blocks; future drag-and-drop / PDF / save-load
  hooks slot in cleanly

## Project layout

```
Soma/
├── app.py                      # Streamlit entry point
├── requirements.txt
├── README.md
└── src/
    ├── document/
    │   ├── builder.py          # Orchestrates Word generation
    │   ├── blocks.py           # Block data models
    │   ├── styles.py           # Custom Word styles
    │   ├── toc.py              # Table of contents field
    │   └── header_footer.py    # Header / footer + page layout
    └── ui/
        ├── components.py       # Streamlit editors per block
        └── state.py            # Session state helpers
```

## Run locally

> Requires Python 3.9+.

```powershell
# 1. (Recommended) create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the UI
streamlit run app.py
```

Streamlit will open `http://localhost:8501` in your browser.

## Using the app

1. In the sidebar, pick a block type and click **➕ Add Block**.
2. Fill in the editor that appears in the main panel. Use the **↑ / ↓**
   buttons to reorder blocks and **Delete** to remove them.
3. Set a file name and click **📄 Generate Document**, then **⬇️ Download
   .docx**.
4. Open the document in Word. When prompted, **update fields** so the
   Table of Contents and page numbers refresh.

## Extending

The architecture is intentionally layered:

- **New block type** — add a dataclass in `src/document/blocks.py`,
  render it in `BPDDocumentBuilder._render_block`, expose an editor in
  `src/ui/components.py`, and add it to the `BlockType` enum.
- **PDF export** — call any `.docx → .pdf` converter on the bytes
  returned by `BPDDocumentBuilder.build()`.
- **Save / load projects** — `state.get_blocks()` returns a JSON-safe
  list (after base64-encoding image bytes) you can persist anywhere.
- **Logo upload** — replace the placeholder run in
  `src/document/header_footer.py` with an image embed.

## Notes

- The TOC field is a real Word field — it shows placeholder text in the
  download until you let Word update fields. We set
  `w:updateFields=true` in document settings, so Word usually prompts
  automatically.
- Only `Heading` and `Subheading` blocks appear in the TOC; the styles
  inherit outline levels 1 and 2 from `Heading 1` / `Heading 2`.
  `Normal Heading` has no outline level so Word excludes it.
