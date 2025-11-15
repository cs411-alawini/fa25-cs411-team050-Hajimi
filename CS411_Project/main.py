import os
from flask import Flask, jsonify, request, render_template_string
import mysql.connector

app = Flask(__name__)

# -------------------------------
# Database config
# -------------------------------
db_config = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
}


def get_db_conn():
    return mysql.connector.connect(**db_config)


# -------------------------------
# Simple front page
# -------------------------------
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Program Explorer</title>
</head>
<body>
    <h1>Program Explorer (GCP + MySQL)</h1>

    <h2>Search Programs by Major & Location</h2>
    <p>
        Major: <input id="majorInput" placeholder="e.g. Computer Science">
        Location: <input id="locationInput" placeholder="e.g. IL">
        <button onclick="search()">Search</button>
    </p>

    <table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <tr>
                <th>ProgramID</th>
                <th>ProgramName</th>
                <th>University</th>
                <th>Location</th>
                <th>Major</th>
                <th>DegreeType</th>
                <th>MedianSalary</th>
            </tr>
        </thead>
        <tbody id="resultBody"></tbody>
    </table>

    <script>
        async function search() {
            const major = document.getElementById('majorInput').value;
            const location = document.getElementById('locationInput').value;
            const params = new URLSearchParams();
            if (major) params.append('major', major);
            if (location) params.append('location', location);

            const res = await fetch('/api/programs/search?' + params.toString());
            const data = await res.json();

            const tbody = document.getElementById('resultBody');
            tbody.innerHTML = '';
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.ProgramID}</td>
                    <td>${row.ProgramName}</td>
                    <td>${row.UniversityName}</td>
                    <td>${row.Location}</td>
                    <td>${row.MajorName}</td>
                    <td>${row.DegreeType || ''}</td>
                    <td>${row.MedianSalary || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


# -------------------------------
# 1.1 Search programs by major & location
# corresponds to:
# WHERE m.MajorName = Major_input AND u.Location = Location_input;
# -------------------------------
@app.route("/api/programs/search", methods=["GET"])
def search_programs():
    major = request.args.get("major")   # Major_input
    location = request.args.get("location")  # Location_input

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
    # 本地跑：python main.py
    app.run(host="0.0.0.0", port=8080, debug=True)
