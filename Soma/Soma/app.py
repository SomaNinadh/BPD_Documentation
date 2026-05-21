"""
BPD Generator — Streamlit entry point.

Run with:  streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from src.document import BPDDocumentBuilder
from src.document.blocks import BlockType
from src.ui import state
from src.ui.components import render_block_card


st.set_page_config(
    page_title="BPD Generator",
    page_icon="📄",
    layout="wide",
)


def _add_block_callback(block_type_value: str) -> None:
    state.add_block(BlockType(block_type_value))


def main() -> None:
    state.init_state()

    st.title("Business Process Document Generator")
    st.caption("Build BPDs block-by-block, then export a polished, on-template .docx.")

    # ---------- Sidebar: add block + actions --------------------------------
    with st.sidebar:
        st.header("Add a block")
        block_type_choice = st.selectbox(
            "Block type",
            options=[b.value for b in BlockType],
            key="add_block_choice",
        )
        st.button(
            "➕ Add Block",
            type="primary",
            use_container_width=True,
            on_click=_add_block_callback,
            args=(block_type_choice,),
        )

        st.divider()
        st.subheader("Document")
        doc_name = st.text_input(
            "File name",
            value=f"BPD_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
            key="doc_filename",
        )

        blocks = state.get_blocks()
        can_generate = bool(blocks)
        generate_clicked = st.button(
            "📄 Generate Document",
            type="primary",
            disabled=not can_generate,
            use_container_width=True,
        )
        if not can_generate:
            st.caption("Add at least one block to enable generation.")

        st.divider()
        st.caption(
            "Tip: when Word opens the document, accept the prompt to update "
            "fields so the Table of Contents reflects the latest headings."
        )

    # ---------- Main: block editors -----------------------------------------
    st.subheader("Document blocks")
    blocks = state.get_blocks()
    if not blocks:
        st.info("No blocks yet — use **Add Block** in the sidebar to begin.")
    else:
        total = len(blocks)
        for idx, block in enumerate(blocks):
            render_block_card(idx, block, total)

    # ---------- Generate ----------------------------------------------------
    if generate_clicked and blocks:
        try:
            builder = BPDDocumentBuilder()
            data = builder.build(state.to_domain_blocks())
        except Exception as exc:  # surface build errors instead of crashing the UI
            st.error(f"Failed to generate document: {exc}")
            return

        filename = doc_name.strip() or "BPD.docx"
        if not filename.lower().endswith(".docx"):
            filename += ".docx"

        st.success("Document generated.")
        st.download_button(
            label="⬇️ Download .docx",
            data=data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
