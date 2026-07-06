import mysql.connector


# ==========================================
# Database Connection
# ==========================================

def connect_db():

    connection = mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
        port= 4000,
        user="3quCSjK73gdUEFX.root",
        password="4BxH0rvrMO4gG6qF",
        database="resume_parser_db"
    )

    return connection


# ==========================================
# Insert One Resume
# ==========================================

def insert_resume(resume):

    connection = connect_db()

    cursor = connection.cursor()

    query = """
    INSERT INTO resumes (

        filename,
        email,
        phone,
        linkedin,
        github,
        websites,
        names,
        organizations,
        locations,
        dates,
        skills,
        degrees,
        institutions,
        graduation_years,
        experience,
        projects,
        certifications

    )

    VALUES (

        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s

    )
    """

    values = (

        resume["filename"],

        resume["contact"]["email"],
        resume["contact"]["phone"],
        resume["contact"]["linkedin"],
        resume["contact"]["github"],
        ", ".join(resume["contact"]["websites"]),

        ", ".join(resume["entities"]["name"]),
        ", ".join(resume["entities"]["organization"]),
        ", ".join(resume["entities"]["location"]),
        ", ".join(resume["entities"]["date"]),

        ", ".join(resume["skills"]),

        ", ".join(resume["education"]["degrees"]),
        ", ".join(resume["education"]["institutions"]),
        ", ".join(resume["education"]["years"]),

        resume["experience"],
        resume["projects"],

        ", ".join(resume["certifications"])

    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# Insert Multiple Resumes
# ==========================================

def insert_multiple_resumes(resumes):

    for resume in resumes:

        insert_resume(resume)


# ==========================================
# Fetch All Resumes
# ==========================================

def fetch_all_resumes():

    connection = connect_db()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM resumes"
    )

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


# ==========================================
# Fetch One Resume
# ==========================================

def fetch_resume(resume_id):

    connection = connect_db()

    cursor = connection.cursor(dictionary=True)

    cursor.execute(

        "SELECT * FROM resumes WHERE id=%s",

        (resume_id,)

    )

    data = cursor.fetchone()

    cursor.close()
    connection.close()

    return data


# ==========================================
# Delete Resume
# ==========================================

def delete_resume(resume_id):

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute(

        "DELETE FROM resumes WHERE id=%s",

        (resume_id,)

    )

    connection.commit()

    cursor.close()
    connection.close()


# ==========================================
# Delete All Resumes
# ==========================================

def delete_all_resumes():

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute(

        "DELETE FROM resumes"

    )

    connection.commit()

    cursor.close()
    connection.close()