"""
Session-state helpers for the Streamlit UI.

Keeps mutation of ``st.session_state`` in one place so the page module
can stay focused on rendering.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

import streamlit as st

from src.document.blocks import (
    BlockType,
    HeadingBlock,
    ImageBlock,
    NormalHeadingBlock,
    ParagraphBlock,
    SubheadingBlock,
    TableBlock,
)


BLOCKS_KEY = "bpd_blocks"


def _new_payload(block_type: BlockType) -> Dict[str, Any]:
    """Default editable payload for each block type."""
    if block_type in (
        BlockType.HEADING,
        BlockType.SUBHEADING,
        BlockType.NORMAL_HEADING,
        BlockType.PARAGRAPH,
    ):
        return {"text": ""}
    if block_type == BlockType.IMAGE:
        return {"image_bytes": None, "filename": "", "width_ratio": 0.7}
    if block_type == BlockType.TABLE:
        rows, cols = 2, 2
        return {
            "rows": rows,
            "cols": cols,
            "data": [["" for _ in range(cols)] for _ in range(rows)],
        }
    raise ValueError(f"Unknown block type: {block_type}")


def init_state() -> None:
    if BLOCKS_KEY not in st.session_state:
        st.session_state[BLOCKS_KEY] = []  # list of {id, type, payload}


def get_blocks() -> List[Dict[str, Any]]:
    return st.session_state[BLOCKS_KEY]


def add_block(block_type: BlockType) -> None:
    st.session_state[BLOCKS_KEY].append(
        {
            "id": uuid.uuid4().hex,
            "type": block_type,
            "payload": _new_payload(block_type),
        }
    )


def remove_block(block_id: str) -> None:
    st.session_state[BLOCKS_KEY] = [b for b in get_blocks() if b["id"] != block_id]


def move_block(block_id: str, direction: int) -> None:
    """direction = -1 for up, +1 for down."""
    blocks = get_blocks()
    idx = next((i for i, b in enumerate(blocks) if b["id"] == block_id), None)
    if idx is None:
        return
    new_idx = idx + direction
    if not 0 <= new_idx < len(blocks):
        return
    blocks[idx], blocks[new_idx] = blocks[new_idx], blocks[idx]


def resize_table(block_id: str, rows: int, cols: int) -> None:
    """Resize the table payload while preserving existing cell text."""
    rows = max(1, int(rows))
    cols = max(1, int(cols))
    for b in get_blocks():
        if b["id"] != block_id:
            continue
        payload = b["payload"]
        old = payload.get("data") or []
        new_data = []
        for r in range(rows):
            row = []
            for c in range(cols):
                if r < len(old) and c < len(old[r]):
                    row.append(old[r][c])
                else:
                    row.append("")
            new_data.append(row)
        payload["rows"] = rows
        payload["cols"] = cols
        payload["data"] = new_data
        return


def to_domain_blocks() -> List[Any]:
    """Convert the UI state into the dataclass blocks the builder expects."""
    domain = []
    for b in get_blocks():
        t = b["type"]
        p = b["payload"]
        if t == BlockType.HEADING:
            domain.append(HeadingBlock(text=p.get("text", "")))
        elif t == BlockType.SUBHEADING:
            domain.append(SubheadingBlock(text=p.get("text", "")))
        elif t == BlockType.NORMAL_HEADING:
            domain.append(NormalHeadingBlock(text=p.get("text", "")))
        elif t == BlockType.PARAGRAPH:
            domain.append(ParagraphBlock(text=p.get("text", "")))
        elif t == BlockType.IMAGE:
            domain.append(
                ImageBlock(
                    image_bytes=p.get("image_bytes"),
                    filename=p.get("filename", ""),
                    width_ratio=float(p.get("width_ratio", 0.7)),
                )
            )
        elif t == BlockType.TABLE:
            domain.append(
                TableBlock(
                    rows=int(p.get("rows", 1)),
                    cols=int(p.get("cols", 1)),
                    data=p.get("data", []),
                )
            )
    return domain
