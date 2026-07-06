import gradio as gr
import pandas as pd

from parser import parse_multiple_resumes

from database import (
    insert_multiple_resumes,
    fetch_all_resumes,
)

# ==========================================================
# THEME
# ==========================================================

theme = gr.themes.Soft()


# ==========================================================
# HELPER FUNCTION
# ==========================================================

def load_dataframe():
    records = fetch_all_resumes()

    if len(records) == 0:
        return pd.DataFrame(
            columns=[
                "ID",
                "Filename",
                "Email",
                "Phone",
                "Skills",
                "Degree",
                "Uploaded At",
            ]
        )

    df = pd.DataFrame(records)

    df = df[
        [
            "id",
            "filename",
            "email",
            "phone",
            "skills",
            "degrees",
            "uploaded_at",
        ]
    ]

    df.columns = [
        "ID",
        "Filename",
        "Email",
        "Phone",
        "Skills",
        "Degree",
        "Uploaded At",
    ]

    return df


# ==========================================================
# PARSE & SAVE
# ==========================================================

def parse_and_save(files):
    if files is None or len(files) == 0:
        return (
            "⚠ Please upload at least one resume.",
            load_dataframe(),
        )

    try:
        file_paths = [file.name for file in files]

        resumes = parse_multiple_resumes(file_paths)

        if len(resumes) == 0:
            return (
                "❌ No valid resumes were parsed.",
                load_dataframe(),
            )

        insert_multiple_resumes(resumes)

        return (
            f"✅ Successfully parsed and stored {len(resumes)} resume(s).",
            load_dataframe(),
        )

    except Exception as e:
        return (
            f"❌ Error: {str(e)}",
            load_dataframe(),
        )


# ==========================================================
# REFRESH TABLE
# ==========================================================

def refresh_table():
    return load_dataframe()


# ==========================================================
# UI
# ==========================================================

with gr.Blocks(theme=theme, title="AI Resume Parser") as app:

    gr.Markdown(
        """
# 📄 AI Resume Parser

Upload multiple resumes, parse them, store them in MySQL and
view all stored resumes.
"""
    )

    gr.Markdown("---")

    upload_files = gr.File(
        label="Upload Resume(s)",
        file_count="multiple",
        file_types=[
            ".pdf",
            ".docx",
            ".txt",
        ],
    )

    with gr.Row():
        parse_button = gr.Button(
            "🚀 Parse & Save",
            variant="primary",
        )

        refresh_button = gr.Button("🔄 Refresh")

    status_box = gr.Textbox(
        label="Status",
        interactive=False,
    )

    gr.Markdown("---")

    resume_table = gr.DataFrame(
        value=load_dataframe(),
        interactive=False,
        label="Stored Resumes",
    )

    app.load(
        fn=load_dataframe,
        outputs=resume_table
    )

    # ==========================================================
    # BUTTON EVENTS
    # ==========================================================

    parse_button.click(
        fn=parse_and_save,
        inputs=upload_files,
        outputs=[
            status_box,
            resume_table,
        ],
    )

    refresh_button.click(
        fn=refresh_table,
        outputs=resume_table,
    )


# ==========================================================
# LAUNCH APP
# ==========================================================

if __name__ == "__main__":
    app.launch()