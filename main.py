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
        host="136.111.138.100",       # 必须有
        user="root",
        password="1234qwer!@#$",
        database="edu_connect",
        port=3306,                         # 必须指定端口
        use_pure=True                      # 强制 TCP，不要 named pipe
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


# -------------------------------
# search programs by major and location, in order to perpare for bookmark function
# -------------------------------
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

    sql = "INSERT INTO Bookmark (UserID, ProgramID) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, program_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "ok"}), 201


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


# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
