import gradio as gr
import pandas as pd
import json

from parser import parse_multiple_resumes

from database import (
    insert_multiple_resumes,
    fetch_all_resumes,
    fetch_resume,
    delete_resume,
    delete_all_resumes
)

# ===========================================================
# THEME
# ===========================================================

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="gray",
)

# ===========================================================
# CUSTOM CSS
# ===========================================================

css = """

.gradio-container{
    max-width:1450px !important;
    margin:auto;
    background:#F8FAFC;
}

.main-title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#1E293B;
    margin-top:10px;
}

.sub-title{
    text-align:center;
    color:#64748B;
    font-size:18px;
    margin-bottom:25px;
}

.card{
    background:white;
    border-radius:14px;
    padding:20px;
    box-shadow:0px 3px 10px rgba(0,0,0,.08);
}

.footer{
    text-align:center;
    color:#94A3B8;
    margin-top:25px;
}

"""

# ===========================================================
# DATABASE HELPERS
# ===========================================================

def get_all_resumes():

    return fetch_all_resumes()


def get_resume(resume_id):

    return fetch_resume(resume_id)


# ===========================================================
# DATAFRAME
# ===========================================================

def dataframe_from_database():

    records = get_all_resumes()

    if len(records) == 0:

        return pd.DataFrame(
            columns=[
                "ID",
                "Filename",
                "Email",
                "Phone",
                "Skills",
                "Degree"
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
            "degrees"
        ]
    ]

    df.columns = [
        "ID",
        "Filename",
        "Email",
        "Phone",
        "Skills",
        "Degree"
    ]

    return df


# ===========================================================
# RESUME JSON
# ===========================================================

def resume_to_json(resume_id):

    if resume_id is None:
        return {}

    resume = get_resume(int(resume_id))

    if resume is None:
        return {}

    return resume


# ===========================================================
# DASHBOARD STATS
# ===========================================================

def get_dashboard_stats():

    records = get_all_resumes()

    total_resumes = len(records)

    total_skills = 0

    latest_upload = "-"

    for row in records:

        if row["skills"]:

            total_skills += len(
                row["skills"].split(",")
            )

    if records:

        latest_upload = str(
            records[-1]["uploaded_at"]
        )

    return {

        "total_resumes": total_resumes,

        "total_skills": total_skills,

        "latest_upload": latest_upload,

        "database_size": total_resumes

    }


# ===========================================================
# UI
# ===========================================================

with gr.Blocks(
    theme=theme,
    css=css,
    title="AI Resume Parser Dashboard"
) as app:

    # =======================================================
    # HEADER
    # =======================================================

    gr.Markdown("""
    <div class="main-title">
        📄 AI Resume Parser Dashboard
    </div>

    <div class="sub-title">
        Upload • Parse • Store • Search • Manage Resumes
    </div>
    """)

    stats = get_dashboard_stats()

    # =======================================================
    # DASHBOARD
    # =======================================================

    with gr.Row():

        total_resume_card = gr.Markdown(
            f"""
### 📄 Total Resumes

# {stats['total_resumes']}
"""
        )

        total_skill_card = gr.Markdown(
            f"""
### 💻 Skills Found

# {stats['total_skills']}
"""
        )

        latest_upload_card = gr.Markdown(
            f"""
### 📅 Last Upload

# {stats['latest_upload']}
"""
        )

        database_card = gr.Markdown(
            f"""
### 🗄 Database Size

# {stats['database_size']}
"""
        )

    gr.Markdown("---")

    # =======================================================
    # UPLOAD SECTION
    # =======================================================

    gr.Markdown("## 📤 Upload Resume(s)")

    uploaded_files = gr.File(
        label="Drag & Drop Resume(s)",
        file_count="multiple",
        file_types=[
            ".pdf",
            ".docx",
            ".txt"
        ],
        height=150
    )

    with gr.Row():

        parse_button = gr.Button(
            "🚀 Parse & Save",
            variant="primary"
        )

        refresh_button = gr.Button(
            "🔄 Refresh",
            variant="secondary"
        )

    upload_status = gr.Textbox(
        label="Status",
        value="Waiting for upload...",
        interactive=False,
        lines=2
    )

    gr.Markdown("---")

    # =======================================================
    # SEARCH
    # =======================================================

    gr.Markdown("## 🔍 Search Resume")

    search_box = gr.Textbox(
        placeholder="Search by filename, email, phone, skill...",
        show_label=False
    )

    gr.Markdown("---")


    # =======================================================
    # RESUME DATABASE
    # =======================================================

    gr.Markdown("## 📋 Resume Database")

    resume_table = gr.DataFrame(
        value=dataframe_from_database(),
        headers=[
            "ID",
            "Filename",
            "Email",
            "Phone",
            "Skills",
            "Degree"
        ],
        interactive=True,
        wrap=True,
        height=350,
        label="Stored Resumes"
    )

    gr.Markdown("---")

    # =======================================================
    # RESUME DETAILS
    # =======================================================

    gr.Markdown("## 📄 Resume Details")

    resume_json = gr.JSON(
        label="Resume Information"
    )

    # Stores currently selected resume ID
    selected_resume_id = gr.State(value=None)

    gr.Markdown("---")

    # =======================================================
    # ACTION BUTTONS
    # =======================================================

    with gr.Row():

        delete_button = gr.Button(
            "🗑 Delete Resume",
            variant="stop",
            scale=1
        )

        clear_database_button = gr.Button(
            "❌ Clear Database",
            variant="stop",
            scale=1
        )

    gr.Markdown("---")

    # =======================================================
    # FOOTER
    # =======================================================

    gr.Markdown(
        """
<div class="footer">

Built with ❤️ using

<b>Python</b> •
<b>spaCy</b> •
<b>Gradio</b> •
<b>MySQL</b>

</div>
"""
    )

# ===========================================================
# UPLOAD & SAVE
# ===========================================================

def upload_and_save(files):

    if not files:

        return (
            "⚠ Please upload at least one resume.",
            dataframe_from_database(),
            *dashboard_components()
        )

    file_paths = [file.name for file in files]

    resumes = parse_multiple_resumes(file_paths)

    insert_multiple_resumes(resumes)

    return (
        f"✅ {len(resumes)} Resume(s) Parsed Successfully.",
        dataframe_from_database(),
        *dashboard_components()
    )


# ===========================================================
# SEARCH
# ===========================================================

def search_resume(keyword):

    keyword = keyword.strip().lower()

    records = fetch_all_resumes()

    if keyword == "":

        return dataframe_from_database()

    filtered = []

    for row in records:

        search_text = " ".join(

            [
        
                str(row["filename"]),
                str(row["email"]),
                str(row["phone"]),
                str(row["skills"]),
                str(row["degrees"]),
                str(row["names"]),
                str(row["organizations"])
        
            ]
        
        ).lower()

        if keyword in search_text:

            filtered.append(row)

    if len(filtered) == 0:

        return pd.DataFrame(
            columns=[
                "ID",
                "Filename",
                "Email",
                "Phone",
                "Skills",
                "Degree"
            ]
        )

    df = pd.DataFrame(filtered)

    df = df[
        [
            "id",
            "filename",
            "email",
            "phone",
            "skills",
            "degrees"
        ]
    ]

    df.columns = [
        "ID",
        "Filename",
        "Email",
        "Phone",
        "Skills",
        "Degree"
    ]

    return df


# ===========================================================
# REFRESH
# ===========================================================

def refresh_database():

    return (
        dataframe_from_database(),
        *dashboard_components()
    )


# ===========================================================
# DASHBOARD COMPONENTS
# ===========================================================

def dashboard_components():

    stats = get_dashboard_stats()

    return (

        f"""
### 📄 Total Resumes

# {stats['total_resumes']}
""",

        f"""
### 💻 Skills Found

# {stats['total_skills']}
""",

        f"""
### 📅 Last Upload

# {stats['latest_upload']}
""",

        f"""
### 🗄 Database Size

# {stats['database_size']}
"""

    )

# ===========================================================
# ROW SELECTION
# ===========================================================

def select_resume(evt: gr.SelectData):

    df = dataframe_from_database()

    row = evt.index[0]

    if row >= len(df):

        return {}, None

    resume_id = int(df.iloc[row]["ID"])

    resume = resume_to_json(resume_id)

    return resume, resume_id


# ===========================================================
# DELETE RESUME
# ===========================================================

def remove_resume(resume_id):

    if resume_id is None:

        return (

            "⚠ No resume selected.",

            dataframe_from_database(),

            {},

            None,

            *dashboard_components()

        )

    delete_resume(int(resume_id))

    return (

        "✅ Resume deleted successfully.",

        dataframe_from_database(),

        {},

        None,

        *dashboard_components()

    )


# ===========================================================
# CLEAR DATABASE
# ===========================================================

def clear_database():

    delete_all_resumes()

    return (

        "✅ Database cleared successfully.",

        dataframe_from_database(),

        {},

        None,

        *dashboard_components()

    )


# ===========================================================
# BUTTON EVENTS
# ===========================================================

parse_button.click(

    fn=upload_and_save,

    inputs=uploaded_files,

    outputs=[

        upload_status,

        resume_table,

        total_resume_card,

        total_skill_card,

        latest_upload_card,

        database_card

    ]

)


refresh_button.click(

    fn=refresh_database,

    outputs=[

        resume_table,

        total_resume_card,

        total_skill_card,

        latest_upload_card,

        database_card

    ]

)


search_box.change(

    fn=search_resume,

    inputs=search_box,

    outputs=resume_table

)


resume_table.select(

    fn=select_resume,

    outputs=[

        resume_json,

        selected_resume_id

    ]

)


delete_button.click(

    fn=remove_resume,

    inputs=selected_resume_id,

    outputs=[

        upload_status,

        resume_table,

        resume_json,

        selected_resume_id,

        total_resume_card,

        total_skill_card,

        latest_upload_card,

        database_card

    ]

)


clear_database_button.click(

    fn=clear_database,

    outputs=[

        upload_status,

        resume_table,

        resume_json,

        selected_resume_id,

        total_resume_card,

        total_skill_card,

        latest_upload_card,

        database_card

    ]

)

# ===========================================================
# INITIALIZE DASHBOARD
# ===========================================================

app.load(
    fn=refresh_database,
    outputs=[
        resume_table,
        total_resume_card,
        total_skill_card,
        latest_upload_card,
        database_card
    ]
)

# ===========================================================
# LAUNCH
# ===========================================================

if __name__ == "__main__":

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

