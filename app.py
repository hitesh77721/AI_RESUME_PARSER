import gradio as gr
import pandas as pd

from parser import parse_multiple_resumes

from database import (
    insert_multiple_resumes,
    fetch_all_resumes,
    delete_resume,
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
            None,   # ✅ CLEAR FILE UPLOADER
        )

    try:
        file_paths = [file.name for file in files]

        resumes = parse_multiple_resumes(file_paths)

        if len(resumes) == 0:
            return (
                "❌ No valid resumes were parsed.",
                load_dataframe(),
                None,   # ✅ CLEAR FILE UPLOADER
            )

        insert_multiple_resumes(resumes)

        return (
            f"✅ Successfully parsed and stored {len(resumes)} resume(s).",
            load_dataframe(),
            None,   # ✅ CLEAR FILE UPLOADER
        )

    except Exception as e:
        return (
            f"❌ Error: {str(e)}",
            load_dataframe(),
            None,   # ✅ CLEAR FILE UPLOADER
        )


# ==========================================================
# REFRESH TABLE
# ==========================================================

def refresh_table():
    return load_dataframe()


# ==========================================================
# DELETE FUNCTION
# ==========================================================

def delete_selected_resume(resume_id):
    try:
        if resume_id is None:
            return "⚠ Please enter a Resume ID.", load_dataframe()

        delete_resume(int(resume_id))

        return "🗑 Resume deleted successfully.", load_dataframe()

    except Exception as e:
        return f"❌ Error: {str(e)}", load_dataframe()


# ==========================================================
# CLEAR UPLOAD FUNCTION (MANUAL)
# ==========================================================

def clear_upload():
    return None


# ==========================================================
# UI
# ==========================================================

with gr.Blocks(theme=theme, title="AI Resume Parser") as app:

    gr.Markdown("""
# 📄 AI Resume Parser

Upload multiple resumes, parse them, store them in MySQL and view all stored resumes.
""")

    gr.Markdown("---")

    # ==========================================================
    # FILE UPLOAD
    # ==========================================================

    upload_files = gr.File(
        label="Upload Resume(s)",
        file_count="multiple",
        file_types=[".pdf", ".docx", ".txt"],
    )

    # ==========================================================
    # BUTTONS
    # ==========================================================

    with gr.Row():
        parse_button = gr.Button("🚀 Parse & Save", variant="primary")
        refresh_button = gr.Button("🔄 Refresh")
        clear_button = gr.Button("🧹 Clear Upload")

    status_box = gr.Textbox(
        label="Status",
        interactive=False,
    )

    gr.Markdown("---")

    # ==========================================================
    # TABLE
    # ==========================================================

    resume_table = gr.DataFrame(
        value=load_dataframe(),
        interactive=False,
        label="Stored Resumes",
    )

    # ==========================================================
    # DELETE UI
    # ==========================================================

    gr.Markdown("## 🗑 Delete Resume")

    with gr.Row():
        delete_id = gr.Number(
            label="Enter Resume ID to Delete",
            precision=0,
        )

        delete_button = gr.Button("Delete", variant="stop")

    # ==========================================================
    # LOAD ON START
    # ==========================================================

    app.load(
        fn=load_dataframe,
        outputs=resume_table
    )

    # ==========================================================
    # EVENTS
    # ==========================================================

    # 🚀 parse + auto clear upload
    parse_button.click(
        fn=parse_and_save,
        inputs=upload_files,
        outputs=[status_box, resume_table, upload_files],
    )

    # 🔄 refresh table
    refresh_button.click(
        fn=refresh_table,
        outputs=resume_table,
    )

    # 🗑 delete resume
    delete_button.click(
        fn=delete_selected_resume,
        inputs=delete_id,
        outputs=[status_box, resume_table],
    )

    # 🧹 manual clear upload
    clear_button.click(
        fn=clear_upload,
        outputs=upload_files,
    )


# ==========================================================
# LAUNCH
# ==========================================================

if __name__ == "__main__":
    app.launch()