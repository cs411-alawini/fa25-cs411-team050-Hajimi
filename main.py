import os
from flask import Flask, jsonify, request, render_template_string, render_template
import mysql.connector

app = Flask(__name__)



# -------------------------------
# Database config
# -------------------------------
# db_config = {
#     "host": os.environ.get("DB_HOST"),
#     "user": os.environ.get("DB_USER"),
#     "password": os.environ.get("DB_PASSWORD"),
#     "database": os.environ.get("DB_NAME"),
# }


# def get_db_conn():
#     return mysql.connector.connect(**db_config)
def get_db_conn():
    return mysql.connector.connect(
        host="136.111.138.100",
        user="root",
        password="1234qwer!@#$",
        database="edu_connect",
        port=3306,
        use_pure=True
    )


# -------------------------------
# Simple front page
# -------------------------------
# INDEX_HTML = """
# <!DOCTYPE html>
# <html>
# <head>
#     <meta charset="utf-8">
#     <title>Program Explorer</title>
# </head>
# <body>
#     <h1>Program Explorer (GCP + MySQL)</h1>

#     <h2>Search Programs by Major & Location</h2>
#     <p>
#         Major: <input id="majorInput" placeholder="e.g. Computer Science">
#         Location: <input id="locationInput" placeholder="e.g. IL">
#         <button onclick="search()">Search</button>
#     </p>

#     <table border="1" cellpadding="5" cellspacing="0">
#         <thead>
#             <tr>
#                 <th>ProgramID</th>
#                 <th>ProgramName</th>
#                 <th>University</th>
#                 <th>Location</th>
#                 <th>Major</th>
#                 <th>DegreeType</th>
#                 <th>MedianSalary</th>
#             </tr>
#         </thead>
#         <tbody id="resultBody"></tbody>
#     </table>

#     <script>
#         async function search() {
#             const major = document.getElementById('majorInput').value;
#             const location = document.getElementById('locationInput').value;
#             const params = new URLSearchParams();
#             if (major) params.append('major', major);
#             if (location) params.append('location', location);

#             const res = await fetch('/api/programs/search?' + params.toString());
#             const data = await res.json();

#             const tbody = document.getElementById('resultBody');
#             tbody.innerHTML = '';
#             data.forEach(row => {
#                 const tr = document.createElement('tr');
#                 tr.innerHTML = `
#                     <td>${row.ProgramID}</td>
#                     <td>${row.ProgramName}</td>
#                     <td>${row.UniversityName}</td>
#                     <td>${row.Location}</td>
#                     <td>${row.MajorName}</td>
#                     <td>${row.DegreeType || ''}</td>
#                     <td>${row.MedianSalary || ''}</td>
#                 `;
#                 tbody.appendChild(tr);
#             });
#         }
#     </script>
# </body>
# </html>
# """


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/login")
def login_page():
    return render_template("login.html")


#--------------------
# admin page, manage and update program
#------------------------

@app.route("/api/programs", methods=["GET"])
def list_programs():
    """
    List all programs with basic info.
    This will be used on the admin page to pick a Program to edit/delete.
    """
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               p.DegreeType, p.MedianSalary,
               p.UniversityID, u.Name AS UniversityName, u.Location,
               p.MajorID, m.MajorName
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        ORDER BY p.ProgramID
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/admin/update-major-jobs", methods=["POST"])
def update_major_jobs_transaction():
    """
    Transaction:
      - Compute AvgMajor
      - Compare with Job1
      - If difference > threshold → remove ALL JobTitle == Job1Title from MajorJob
        then insert Job2
    """
    data = request.json or {}
    major_id  = data.get("major_id")
    job1_id   = data.get("job1")
    job2_id   = data.get("job2")
    threshold = float(data.get("threshold", 15000))

    if not major_id or not job1_id or not job2_id:
        return jsonify({"error": "major_id, job1, job2 are required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction(isolation_level="READ COMMITTED")

        # --------------------------------------------------
        # Ensure Job1 / Job2 exist
        # --------------------------------------------------
        cursor.execute("""
            SELECT JobID, JobTitle, AvgSalary
            FROM Job
            WHERE JobID IN (%s, %s)
        """, (job1_id, job2_id))
        jobs = cursor.fetchall()
        if len(jobs) != 2:
            conn.rollback()
            return jsonify({"error": "Job1 or Job2 does not exist"}), 400

        job_info = {j["JobID"]: j for j in jobs}
        job1 = job_info[job1_id]
        job2 = job_info[job2_id]

        # --------------------------------------------------
        # Job1 must currently be linked
        # --------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM MajorJob
            WHERE MajorID = %s AND JobID = %s
        """, (major_id, job1_id))
        if cursor.fetchone()["cnt"] == 0:
            conn.rollback()
            return jsonify({"error": "Job1 is not currently linked to this major"}), 400

        # --------------------------------------------------
        # Compute major average salary (Avg of all job salaries)
        # --------------------------------------------------
        cursor.execute("""
            SELECT AVG(j.AvgSalary) AS avg_major
            FROM MajorJob mj
            JOIN Job j ON mj.JobID = j.JobID
            WHERE mj.MajorID = %s
        """, (major_id,))
        avg_major = cursor.fetchone()["avg_major"]

        avg_job1 = job1["AvgSalary"]
        avg_job2 = job2["AvgSalary"]
        diff = abs(avg_major - avg_job1)
        switched = False

        # If difference > threshold → delete ALL Job1Title jobs
        if diff > float(threshold):
            job1_title = job1["JobTitle"]
            job2_title = job2["JobTitle"]

            cursor.execute("SELECT JobID FROM Job WHERE JobTitle = %s", (job1_title,))
            job1_ids = [row["JobID"] for row in cursor.fetchall()]

            cursor.execute("SELECT JobID FROM Job WHERE JobTitle = %s", (job2_title,))
            job2_ids = [row["JobID"] for row in cursor.fetchall()]

            if job1_ids:
                del_placeholders = ",".join(["%s"] * len(job1_ids))
                cursor.execute(
                    f"DELETE FROM MajorJob WHERE MajorID = %s AND JobID IN ({del_placeholders})",
                    [major_id] + job1_ids
                )

            for jid in job2_ids:
                cursor.execute(
                    "INSERT IGNORE INTO MajorJob(MajorID, JobID) VALUES (%s, %s)",
                    (major_id, jid)
                )

            switched = True

        # Get major name
        cursor.execute("SELECT MajorName FROM Major WHERE MajorID = %s", (major_id,))
        major_name = cursor.fetchone()["MajorName"]

        conn.commit()

        return jsonify({
            "status": "ok",
            "switched": switched,
            "threshold": threshold,
            "diff_major_job1": diff,
            "major": {
                "id": major_id,
                "name": major_name,
                "avg_salary": avg_major
            },
            "job1": {
                "id": job1_id,
                "title": job1["JobTitle"],
                "avg_salary": avg_job1
            },
            "job2": {
                "id": job2_id,
                "title": job2["JobTitle"],
                "avg_salary": avg_job2
            }
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route("/api/admin/major-jobs/<int:major_id>", methods=["GET"])
def get_major_jobs(major_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT j.JobID, j.JobTitle
        FROM MajorJob mj
        JOIN Job j ON mj.JobID = j.JobID
        WHERE mj.MajorID = %s
        ORDER BY j.JobTitle;
    """
    cursor.execute(sql, (major_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)





@app.route("/api/programs", methods=["POST"])
def create_program():
    """
    Create a new program.
    Required JSON fields: name, university_id, major_id, degree_type, median_salary
    """
    data = request.json or {}
    name = data.get("name")
    university_id = data.get("university_id")
    major_id = data.get("major_id")
    degree_type = data.get("degree_type")
    median_salary = data.get("median_salary")

    if not all([name, university_id, major_id, degree_type]) or median_salary is None:
        return jsonify({
            "error": "name, university_id, major_id, degree_type, median_salary are required"
        }), 400

    conn = get_db_conn()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO Program (Name, UniversityID, MajorID, DegreeType, MedianSalary)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (name, university_id, major_id, degree_type, median_salary))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return get_program(new_id), 201


@app.route("/api/programs/<int:program_id>", methods=["GET"])
def get_program(program_id):
    """
    Get a single program by ID.
    """
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               p.DegreeType, p.MedianSalary,
               p.UniversityID, u.Name AS UniversityName, u.Location, u.Tuition,
               p.MajorID, m.MajorName
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        WHERE p.ProgramID = %s
    """
    cursor.execute(sql, (program_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": "Program not found"}), 404
    return jsonify(row)


@app.route("/api/programs/<int:program_id>", methods=["PUT"])
def update_program(program_id):
    """
    Update a program.
    Accepts partial updates: only fields present in JSON will be updated.
    Allowed fields: name, university_id, major_id, degree_type, median_salary
    """
    data = request.json or {}
    fields = []
    params = []

    if "name" in data:
        fields.append("Name = %s")
        params.append(data["name"])
    if "university_id" in data:
        fields.append("UniversityID = %s")
        params.append(data["university_id"])
    if "major_id" in data:
        fields.append("MajorID = %s")
        params.append(data["major_id"])
    if "degree_type" in data:
        fields.append("DegreeType = %s")
        params.append(data["degree_type"])
    if "median_salary" in data:
        fields.append("MedianSalary = %s")
        params.append(data["median_salary"])

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    params.append(program_id)

    conn = get_db_conn()
    cursor = conn.cursor()
    sql = "UPDATE Program SET " + ", ".join(fields) + " WHERE ProgramID = %s"
    cursor.execute(sql, tuple(params))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Program not found"}), 404

    return get_program(program_id)


@app.route("/api/programs/<int:program_id>", methods=["DELETE"])
def delete_program(program_id):
    """
    Delete a program by ID.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    sql = "DELETE FROM Program WHERE ProgramID = %s"
    cursor.execute(sql, (program_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Program not found"}), 404
    return jsonify({"status": "deleted"})


# search programs by major and location, in order to perpare for bookmark function
@app.route("/api/programs/keyword-search", methods=["GET"])
def keyword_search_programs():
    """
    Keyword-based search across Program name, Major name, University name, and University location.
    Query parameter: q
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400

    pattern = f"%{q}%"

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               u.Name AS UniversityName, u.Location,
               m.MajorName, p.DegreeType, p.MedianSalary
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        WHERE p.Name      LIKE %s
           OR m.MajorName LIKE %s
           OR u.Name      LIKE %s
           OR u.Location  LIKE %s
        ORDER BY p.ProgramID
    """
    cursor.execute(sql, (pattern, pattern, pattern, pattern))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)
    
@app.route("/api/programs/search", methods=["GET"])
def search_programs():
    major = request.args.get("major")
    location = request.args.get("location")
    min_salary = request.args.get("min_salary", type=int)

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    base_sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               u.Name AS UniversityName, u.Location,
               m.MajorName, p.DegreeType, p.MedianSalary
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        WHERE 1=1
    """
    params = []
    if major:
        base_sql += " AND m.MajorName = %s"
        params.append(major)
    if location:
        base_sql += " AND u.Location = %s"
        params.append(location)
    if min_salary is not None:
        base_sql += " AND p.MedianSalary >= %s"
        params.append(min_salary)

    base_sql += " ORDER BY p.ProgramID"
    cursor.execute(base_sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------------
# 1.2 Filter programs by tuition & salary
# WHERE u.Tuition < Max_Tuition_input AND p.MedianSalary > Min_Salary_input
# -------------------------------
@app.route("/api/programs/filter", methods=["GET"])
def filter_programs():
    max_tuition = request.args.get("max_tuition", type=int)
    min_salary = request.args.get("min_salary", type=int)

    if max_tuition is None or min_salary is None:
        return jsonify({"error": "max_tuition and min_salary are required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               u.Name AS UniversityName, u.Tuition,
               p.MedianSalary
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        WHERE u.Tuition < %s
          AND p.MedianSalary > %s
        ORDER BY p.MedianSalary DESC
    """
    cursor.execute(sql, (max_tuition, min_salary))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------------
# 1.3 List all programs for a given university
# WHERE u.Name = University_Name_input
# -------------------------------
@app.route("/api/programs/by-university", methods=["GET"])
def programs_by_university():
    uni_name = request.args.get("university_name")
    if not uni_name:
        return jsonify({"error": "university_name is required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               m.MajorName, p.DegreeType, p.MedianSalary
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        WHERE u.Name = %s
        ORDER BY p.ProgramID
    """
    cursor.execute(sql, (uni_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------------
# 1.4 Program details + related jobs
# WHERE p.ProgramID = Program_ID_input
# -------------------------------
@app.route("/api/programs/<int:program_id>/details", methods=["GET"])
def program_details(program_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               u.Name AS UniversityName, u.Location,
               m.MajorName, m.Field,
               j.JobID, j.JobTitle, j.Company,
               j.Location AS JobLocation, j.AvgSalary
        FROM Program p
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        JOIN MajorJob mj  ON m.MajorID = mj.MajorID
        JOIN Job j        ON mj.JobID = j.JobID
        WHERE p.ProgramID = %s
    """
    cursor.execute(sql, (program_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------------
# 2.1 Jobs related to a major
# WHERE m.MajorName = Major_Name_input
# -------------------------------
@app.route("/api/majors/<major_name>/jobs", methods=["GET"])
def jobs_for_major(major_name):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT j.JobID, j.JobTitle, j.Company, j.Location, j.AvgSalary
        FROM Major m
        JOIN MajorJob mj ON m.MajorID = mj.MajorID
        JOIN Job j       ON mj.JobID = j.JobID
        WHERE m.MajorName = %s
    """
    cursor.execute(sql, (major_name,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# -------------------------------
# 3.1 Set user's preferred major & job
# UPDATE `User`
# SET PreferredMajor = Major_ID_input, PreferredJob = Job_ID_input
# WHERE UserID = User_ID_input;
# -------------------------------
@app.route("/api/users/<int:user_id>/preferences", methods=["POST"])
def set_user_preferences(user_id):
    data = request.json or {}
    major_id = data.get("preferred_major_id")
    job_id = data.get("preferred_job_id")

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = """
        UPDATE `User`
        SET PreferredMajor = %s,
            PreferredJob   = %s
        WHERE UserID = %s
    """
    cursor.execute(sql, (major_id, job_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "ok"})


# -------------------------------
# 4.1 / 4.2 / 4.3 Bookmarks
# -------------------------------

# 4.1 Add bookmark
@app.route("/api/bookmarks", methods=["POST"])
def add_bookmark():
    data = request.json or {}
    user_id = data.get("user_id")
    program_id = data.get("program_id")
    if not user_id or not program_id:
        return jsonify({"error": "user_id and program_id are required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "INSERT IGNORE INTO Bookmark (UserID, ProgramID) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, program_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "ok"}), 201

# # -------------------------------
# # 4.x Transaction: auto-bookmark top N recommended programs for a user
# # -------------------------------
# @app.route("/api/users/<int:user_id>/auto-bookmark", methods=["POST"])
# def auto_bookmark_for_user(user_id):
#     """
#     Transaction:
#       1) Based on User.PreferredMajor / PreferredJob and a min_salary,
#          use a multi-table JOIN + GROUP BY + ORDER BY + LIMIT
#          to pick top N candidate programs.
#       2) Compute aggregate stats (e.g., avg median salary) for these programs.
#       3) Insert them into Bookmark in the same transaction (INSERT IGNORE
#          to avoid duplicates).
#       4) COMMIT if all succeed; ROLLBACK on error.
#     """
#     data = request.json or {}
#     min_salary = data.get("min_salary", 60000)
#     top_n = data.get("top_n", 5)

#     conn = get_db_conn()
#     cursor = conn.cursor()

#     try:
#         conn.start_transaction(isolation_level="READ COMMITTED")

#         sql_candidates = """
#             SELECT
#                 p.ProgramID,
#                 p.MedianSalary
#             FROM `User` u_pref
#             JOIN Program p
#               ON (u_pref.PreferredMajor IS NULL OR u_pref.PreferredMajor = p.MajorID)
#             JOIN University u
#               ON u.UniversityID = p.UniversityID
#             JOIN Major m
#               ON m.MajorID = p.MajorID
#             LEFT JOIN MajorJob mj
#               ON mj.MajorID = m.MajorID
#             LEFT JOIN Job j
#               ON j.JobID = mj.JobID
#             WHERE u_pref.UserID = %s
#               AND p.MedianSalary >= %s
#               AND (
#                     u_pref.PreferredJob IS NULL
#                     OR j.JobTitle = (
#                             SELECT JobTitle 
#                             FROM Job 
#                             WHERE JobID = u_pref.PreferredJob
#                         )
#                 )
#             GROUP BY p.ProgramID, p.MedianSalary
#             ORDER BY p.MedianSalary DESC
#             LIMIT %s
#         """
#         cursor.execute(sql_candidates, (user_id, min_salary, top_n))
#         rows = cursor.fetchall()

#         if not rows:
#             conn.rollback()
#             cursor.close()
#             conn.close()
#             return jsonify({
#                 "status": "no_candidates",
#                 "message": "No programs match user's preference under given min_salary."
#             }), 200

#         program_ids = [r[0] for r in rows]

#         placeholders = ",".join(["%s"] * len(program_ids))
#         sql_stats = f"""
#             SELECT
#                 AVG(MedianSalary) AS AvgMedianSalary,
#                 COUNT(*)          AS Cnt
#             FROM Program
#             WHERE ProgramID IN ({placeholders})
#         """
#         cursor.execute(sql_stats, program_ids)
#         stats_row = cursor.fetchone()
#         avg_salary = stats_row[0] if stats_row and stats_row[0] is not None else None
#         cnt = stats_row[1] if stats_row else 0

#         insert_sql = """
#             INSERT IGNORE INTO Bookmark (UserID, ProgramID)
#             VALUES (%s, %s)
#         """
#         inserted = 0
#         for pid in program_ids:
#             cursor.execute(insert_sql, (user_id, pid))
#             inserted += cursor.rowcount  # 1=新插入，0=已存在被忽略
#         conn.commit()

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "ok",
#             "user_id": user_id,
#             "selected_count": len(program_ids),
#             "inserted_count": inserted,
#             "avg_median_salary": float(avg_salary) if avg_salary is not None else None,
#             "program_ids": program_ids
#         }), 201

#     except Exception as e:
#         # 任意一步出错就回滚
#         conn.rollback()
#         cursor.close()
#         conn.close()
#         return jsonify({"error": str(e)}), 500


# 4.2 Remove bookmark
@app.route("/api/bookmarks", methods=["DELETE"])
def remove_bookmark():
    data = request.json or {}
    user_id = data.get("user_id")
    program_id = data.get("program_id")
    if not user_id or not program_id:
        return jsonify({"error": "user_id and program_id are required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "DELETE FROM Bookmark WHERE UserID = %s AND ProgramID = %s"
    cursor.execute(sql, (user_id, program_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "ok"})


# 4.3 Get all bookmarked programs for a user
@app.route("/api/users/<int:user_id>/bookmarks", methods=["GET"])
def get_user_bookmarks(user_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT p.ProgramID, p.Name AS ProgramName,
               u.Name AS UniversityName, m.MajorName,
               p.DegreeType, p.MedianSalary
        FROM Bookmark b
        JOIN Program p    ON b.ProgramID = p.ProgramID
        JOIN University u ON p.UniversityID = u.UniversityID
        JOIN Major m      ON p.MajorID = m.MajorID
        WHERE b.UserID = %s
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

#  4.4 Clear all bookmarks for a user
@app.route("/api/users/<int:user_id>/bookmarks", methods=["DELETE"])
def clear_user_bookmarks(user_id):
    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "DELETE FROM Bookmark WHERE UserID = %s"
    cursor.execute(sql, (user_id,))
    deleted = cursor.rowcount

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "ok", "deleted": deleted})

# -------------------------------
# 6.1 Analytics: Average salary by major
# -------------------------------
@app.route("/api/analytics/avg-salary-by-major", methods=["GET"])
def avg_salary_by_major():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT m.MajorName, AVG(p.MedianSalary) AS AvgMedianSalary
        FROM Major m
        JOIN Program p ON m.MajorID = p.MajorID
        GROUP BY m.MajorName
        ORDER BY AvgMedianSalary DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


# ----------------------------------------------
# New Feature: Personalized Program Recommendations (stored procedure)
# ----------------------------------------------
# 
@app.route("/api/admin/create_procedures", methods=["POST"])
def create_stored_procedures():
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("DROP PROCEDURE IF EXISTS RecommendProgramsForUser")

    create_sql = """
        DROP PROCEDURE IF EXISTS RecommendProgramsForUser;
        DELIMITER $$

        CREATE PROCEDURE RecommendProgramsForUser(
            IN p_user_id INT,
            IN p_max_tuition INT,
            IN p_min_salary INT
        )
        mainBlock:BEGIN
            DECLARE v_majorName VARCHAR(255);
            DECLARE v_count INT DEFAULT 0;

            SELECT m.MajorName
            INTO v_majorName
            FROM User u
            JOIN Major m ON m.MajorID = u.PreferredMajor
            WHERE u.UserID = p_user_id
            LIMIT 1;

            IF v_majorName IS NULL THEN
                SELECT * FROM Program WHERE 1=0;
                LEAVE mainBlock;
            END IF;

            DROP TEMPORARY TABLE IF EXISTS TempBase;
            CREATE TEMPORARY TABLE TempBase AS
            SELECT 
                p.ProgramID,
                p.Name AS ProgramName,
                m.MajorName,
                u.Name AS UniversityName,
                p.MedianSalary,
                u.Tuition,
                p.DegreeType,

                (
                    SELECT AVG(u2.Tuition)
                    FROM Program p2
                    JOIN University u2 ON u2.UniversityID = p2.UniversityID
                    WHERE p2.MajorID = p.MajorID
                ) AS AvgTuitionForMajor

            FROM Program p
            JOIN Major m ON m.MajorID = p.MajorID
            JOIN University u ON u.UniversityID = p.UniversityID
            WHERE m.MajorName = v_majorName
            ORDER BY p.MedianSalary DESC;

            SELECT COUNT(*) INTO v_count
            FROM TempBase
            WHERE Tuition <= p_max_tuition
            AND MedianSalary >= p_min_salary;

            IF v_count = 0 THEN

                DROP TEMPORARY TABLE IF EXISTS TempResult;
                CREATE TEMPORARY TABLE TempResult AS
                (
                    SELECT * FROM TempBase
                    ORDER BY MedianSalary DESC
                    LIMIT 5
                )
                UNION
                (
                    SELECT
                        p.ProgramID,
                        p.Name AS ProgramName,
                        m.MajorName,
                        u.Name AS UniversityName,
                        p.MedianSalary,
                        u.Tuition,
                        p.DegreeType,

                        (
                            SELECT AVG(u2.Tuition)
                            FROM Program p2
                            JOIN University u2 ON u2.UniversityID = p2.UniversityID
                            WHERE p2.MajorID = p.MajorID
                        ) AS AvgTuitionForMajor

                    FROM Program p
                    JOIN Major m ON m.MajorID = p.MajorID
                    JOIN University u ON u.UniversityID = p.UniversityID
                    ORDER BY p.MedianSalary DESC
                    LIMIT 5
                );

                SELECT * FROM TempResult ORDER BY MedianSalary DESC;

            ELSE
                SELECT
                    ProgramID,
                    ProgramName,
                    UniversityName,
                    MajorName,
                    DegreeType,
                    MedianSalary,
                    Tuition,
                    AvgTuitionForMajor
                FROM TempBase
                WHERE Tuition <= p_max_tuition
                AND MedianSalary >= p_min_salary
                ORDER BY MedianSalary DESC;

            END IF;

        END$$
        DELIMITER ;

    """

    cursor.execute(create_sql)

    conn.commit()
    cursor.close()
    conn.close()
    print("=== DEBUG SQL START ===")
    print(create_sql)
    print("=== DEBUG SQL END ===")

    return jsonify({"status": "Stored procedure created successfully!"})



#----------------------------------------------
# Call the stored procedure to get recommended programs for a user
#----------------------------------------------
@app.route("/api/users/<int:user_id>/recommend", methods=["GET"])
def call_recommend_procedure(user_id):
    # Read min_salary from query string
    min_salary = request.args.get("min_salary", default=60000, type=int)
    max_tuition = request.args.get("max_tuition", default=999999, type=int)

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Call the stored procedure
        cursor.callproc("RecommendProgramsForUser", [user_id, max_tuition, min_salary])

        # 2. Collect result set
        results = []
        stored = getattr(cursor, "stored_results", None)

        # 2. Collect result set
        results = []

        stored_attr = getattr(cursor, "stored_results", None)

        # Newer versions treat stored_results as a property (not a function)
        if not callable(stored_attr):
            # stored_results is a property (future behavior)
            for result in cursor.stored_results:
                results = result.fetchall()
        else:
            # stored_results is a deprecated method (current behavior)
            for result in cursor.stored_results():
                results = result.fetchall()



        return jsonify(results)

    except Exception as e:
        print("Error calling stored procedure:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

## ----------------------------------------------
## new feature: load user comparisons
## ----------------------------------------------
@app.route("/api/comparisons/<int:user_id>", methods=["GET"])
def get_user_comparisons(user_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT c.ComparisonID,
               c.NoteFromUser,
               c.ProgramID1, p1.Name AS Program1Name,
               c.ProgramID2, p2.Name AS Program2Name
        FROM Comparison c
        JOIN Program p1 ON c.ProgramID1 = p1.ProgramID
        JOIN Program p2 ON c.ProgramID2 = p2.ProgramID
        WHERE c.UserID = %s
        ORDER BY c.ComparisonID DESC;
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/comparisons", methods=["POST"])
def save_comparison():
    data = request.get_json()
    user_id = data.get("user_id")
    pid1 = data.get("program1_id")
    pid2 = data.get("program2_id")
    note = data.get("note", "")

    if not (user_id and pid1 and pid2):
        return jsonify({"error": "Two programs must be selected"}), 400

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = """
        INSERT INTO Comparison(UserID, ProgramID1, ProgramID2, NoteFromUser)
        VALUES (%s, %s, %s, %s);
    """

    cursor.execute(sql, (user_id, pid1, pid2, note))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "Comparison saved"})

@app.route("/api/comparisons/<int:comparison_id>", methods=["DELETE"])
def delete_comparison(comparison_id):
    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "DELETE FROM Comparison WHERE ComparisonID = %s"
    cursor.execute(sql, (comparison_id,))
    conn.commit()

    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Comparison not found"}), 404

    return jsonify({"status": "deleted"})

# -------------------------------
# New Feature: Trigger, if add a program with low salary, add it to alert table
# """
# DROP TRIGGER IF EXISTS salary_alert_trigger;

# DELIMITER //
# CREATE TRIGGER salary_alert_trigger
# AFTER INSERT ON Bookmark
# FOR EACH ROW
# BEGIN
#     DECLARE salary INT;
#     DECLARE pname VARCHAR(255);
#     DECLARE nextID INT;

#     SELECT MedianSalary, Name 
#     INTO salary, pname
#     FROM Program
#     WHERE ProgramID = NEW.ProgramID;

#     SELECT IFNULL(MAX(AlertID), 0) + 1
#     INTO nextID
#     FROM Alert
#     WHERE UserID = NEW.UserID;

#     IF salary < 60000 THEN
#         INSERT INTO Alert(AlertID, UserID, Message)
#         VALUES (
#             nextID,
#             NEW.UserID,
#             CONCAT('You bookmarked a low-salary program: ', pname)
#         );
#     END IF;

# END;
# //
# DELIMITER ;
# """



# Get all alerts for a user
@app.route("/api/users/<int:user_id>/alerts", methods=["GET"])
def get_alerts(user_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT AlertID, UserID, Message
        FROM Alert
        WHERE UserID = %s
        ORDER BY AlertID DESC
    """

    cursor.execute(sql, (user_id,))
    alerts = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(alerts)

# Delete a specific alert
@app.route("/api/users/<int:user_id>/alerts/<int:alert_id>", methods=["DELETE"])
def delete_alert(user_id, alert_id):
    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "DELETE FROM Alert WHERE UserID = %s AND AlertID = %s"
    cursor.execute(sql, (user_id, alert_id))
    conn.commit()

    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Alert not found"}), 404

    return jsonify({"status": "deleted"})

# connect to alert page
@app.route("/alert")
def alert_page():
    return render_template("alert.html")


### -------------------------------
# login page
### -------------------------------
@app.route("/api/login", methods=["POST"])
def login_user():
    """
    Simple login using User.Username + User.PasswordHash (作为明文密码使用就行).
    Request JSON: { "username": "...", "password": "..." }
    Response:
      - 200: { "status": "success", "user_id": ..., "username": "..." }
      - 401: { "status": "fail", "error": "Invalid username or password" }
    """
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT UserID, Username
        FROM User
        WHERE Username = %s AND PasswordHash = %s
    """
    cursor.execute(sql, (username, password))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return jsonify({
            "status": "success",
            "user_id": row["UserID"],
            "username": row["Username"]
        })
    else:
        return jsonify({
            "status": "fail",
            "error": "Invalid username or password"
        }), 401



### -------------------------------
# New Feature: User info
### -------------------------------
@app.route("/api/users/<int:user_id>/info", methods=["GET"])
def get_user_info(user_id):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            u.UserID,
            u.Username,
            u.Email,
            u.PreferredLocation,

            u.PreferredMajor,
            m.MajorName,

            u.PreferredJob,
            j.JobTitle

        FROM User u
        LEFT JOIN Major m ON u.PreferredMajor = m.MajorID
        LEFT JOIN Job j   ON u.PreferredJob = j.JobID
        WHERE u.UserID = %s
    """
    
    cursor.execute(sql, (user_id,))
    info = cursor.fetchone()

    cursor.close()
    conn.close()

    if info:
        return jsonify({
            "UserID": info["UserID"],
            "Username": info["Username"],
            "Email": info["Email"],
            "PreferredLocation": info["PreferredLocation"],

            "PreferredMajor": info["MajorName"] or "(none)",
            "PreferredJob": info["JobTitle"] or "(none)",

            "PreferredMajorID": info["PreferredMajor"],
            "PreferredJobID": info["PreferredJob"]
        })

    return jsonify({"error": "User not found"}), 404


@app.route("/api/users/<int:user_id>/password", methods=["PUT"])
def update_password(user_id):
    data = request.json or {}
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "Password required"}), 400

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = "UPDATE User SET PasswordHash = %s WHERE UserID = %s"
    cursor.execute(sql, (new_password, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "password_updated"})

@app.route("/userinfo")
def userinfo_page():
    return render_template("userinfo.html")

@app.route("/api/majors", methods=["GET"])
def list_majors():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT MajorID, MajorName
        FROM Major
        ORDER BY MajorName;
    """

    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(rows)



@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT MIN(JobID) AS JobID, JobTitle
        FROM Job
        GROUP BY JobTitle
        ORDER BY JobTitle;
    """

    cursor.execute(sql)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(rows)



@app.route("/api/users/<int:user_id>/preferences", methods=["PUT"])
def update_user_preferences(user_id):
    data = request.json or {}
    major_id = data.get("preferred_major")
    job_id = data.get("preferred_job")

    conn = get_db_conn()
    cursor = conn.cursor()

    sql = """
        UPDATE User
        SET PreferredMajor = %s,
            PreferredJob   = %s
        WHERE UserID = %s
    """

    cursor.execute(sql, (major_id, job_id, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"status": "updated"})

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
