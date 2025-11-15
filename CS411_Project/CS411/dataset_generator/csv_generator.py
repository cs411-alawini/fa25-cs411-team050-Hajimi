import csv
import random
from faker import Faker

fake = Faker()

# =========================
# CONFIG (scaled up)
# =========================
N_MAJORS = 30
N_JOBS = 1000
N_UNIS = 80
N_PROGRAMS = 1000
N_USERS = 1000

# dependent tables
N_COMPARISONS = 1500
N_BOOKMARKS = 3000
N_MAJOR_JOB = 2000
N_USER_JOB_PREF = 3000
N_USER_MAJOR_PREF = 3000

# =========================
# STORAGE
# =========================
majors = []
jobs = []
universities = []
programs = []
users = []
comparisons = []
bookmarks = []
major_jobs = []
user_job_prefs = []
user_major_prefs = []

# =========================
# 1. Major
# =========================
majors = []

# 真实存在的30个专业和对应领域
major_list = [
    ("Computer Science", "STEM"),
    ("Electrical Engineering", "STEM"),
    ("Mechanical Engineering", "STEM"),
    ("Business Administration", "Business"),
    ("Data Science", "STEM"),
    ("Psychology", "Social Science"),
    ("Civil Engineering", "STEM"),
    ("Biomedical Engineering", "STEM"),
    ("Finance", "Business"),
    ("Economics", "Social Science"),
    ("Accounting", "Business"),
    ("Marketing", "Business"),
    ("Industrial Engineering", "STEM"),
    ("Chemical Engineering", "STEM"),
    ("English Literature", "Humanities"),
    ("History", "Humanities"),
    ("Management Information Systems", "Business"),
    ("Supply Chain Management", "Business"),
    ("Entrepreneurship", "Business"),
    ("Philosophy", "Humanities"),
    ("Sociology", "Social Science"),
    ("Political Science", "Social Science"),
    ("Communication Studies", "Humanities"),
    ("International Relations", "Social Science"),
    ("Human Resource Management", "Business"),
    ("Statistics", "STEM"),
    ("Environmental Engineering", "STEM"),
    ("Materials Science and Engineering", "STEM"),
    ("Applied Mathematics", "STEM"),
    ("Linguistics", "Humanities"),
]

# 生成带ID的专业元组 (MajorID, MajorName, Field)
for i, (name, field) in enumerate(major_list, start=1):
    majors.append((i, name, field))

# =========================
# 2. Job (1000)
# =========================
job_title_pool = [
    "Software Engineer", "Data Analyst", "Product Manager", "Electrical Engineer",
    "Mechanical Engineer", "Research Assistant", "Consultant", "Business Analyst",
    "Data Scientist", "System Architect", "Network Engineer", "ML Engineer",
    "UX Designer", "Hardware Engineer", "Cloud Engineer", "DevOps Engineer",
    "Test Engineer", "Project Coordinator", "Operations Analyst", "Security Engineer"
]

for i in range(1, N_JOBS + 1):
    title = random.choice(job_title_pool)
    company = fake.company()
    location = fake.city()
    avg_salary = random.randint(60000, 180000)
    jobs.append((i, title, company, location, avg_salary))

# =========================
# 3. University (80)
# =========================
regions = ["Midwest", "Northeast", "South", "West", "International"]

for i in range(1, N_UNIS + 1):
    name = f"{fake.city()} University"
    location = fake.city()
    region = random.choice(regions)
    tuition = random.randint(15000, 75000)
    universities.append((i, name, location, region, tuition))

# =========================
# 4. Program (1000)
# =========================
degree_types = ["BS", "MS", "PhD", "BEng", "MEng", "MBA"]
program_name_pool = [
    "B.S. in Computer Science",
    "B.S. in Electrical Engineering",
    "B.S. in Mechanical Engineering",
    "B.S. in Civil Engineering",
    "B.S. in Industrial Engineering",
    "B.S. in Biomedical Engineering",
    "B.S. in Materials Science and Engineering",
    "B.S. in Environmental Engineering",
    "B.S. in Data Science",
    "B.S. in Applied Mathematics",
    "B.A. in Economics",
    "B.A. in Psychology",
    "B.A. in Sociology",
    "B.A. in History",
    "B.A. in Linguistics",
    "B.A. in Philosophy",
    "B.A. in International Relations",
    "B.A. in Communication Studies",
    "B.B.A. in Finance",
    "B.B.A. in Accounting",
    "B.B.A. in Marketing",
    "B.B.A. in Supply Chain Management",
    "M.S. in Computer Science",
    "M.S. in Electrical and Computer Engineering",
    "M.S. in Mechanical Engineering",
    "M.S. in Civil and Environmental Engineering",
    "M.S. in Industrial Engineering",
    "M.S. in Data Science",
    "M.S. in Statistics",
    "M.S. in Finance",
    "M.S. in Business Analytics",
    "M.Eng. in Electrical Engineering",
    "M.Eng. in Mechanical Engineering",
    "M.Eng. in Materials Science",
    "MBA in Strategic Management",
    "MBA in Operations Management",
    "MBA in Marketing",
    "MBA in Entrepreneurship",
    "Ph.D. in Computer Science",
    "Ph.D. in Electrical Engineering",
    "Ph.D. in Mechanical Engineering",
    "Ph.D. in Economics",
    "Ph.D. in Psychology",
]

programs = []
for i in range(1, N_PROGRAMS + 1):
    uni_id = random.choice(universities)[0]
    major_id = random.choice(majors)[0]
    median_salary = random.randint(50000, 150000)
    degree_type = random.choice(degree_types)
    program_name = random.choice(program_name_pool)
    programs.append((i, program_name, uni_id, major_id, median_salary, degree_type))

# =========================
# 5. User (1000)
# =========================
for i in range(1, N_USERS + 1):
    username = fake.user_name()
    email = fake.email()
    password_hash = fake.sha256()
    preferred_major = random.choice(majors)[0]
    preferred_job = random.choice(jobs)[0]
    preferred_location = fake.city()
    users.append((i, username, email, password_hash, preferred_major, preferred_location, preferred_job))

# =========================
# 6. MajorJob
# =========================
seen_pairs = set()
while len(major_jobs) < N_MAJOR_JOB:
    m = random.choice(majors)[0]
    j = random.choice(jobs)[0]
    if (m, j) not in seen_pairs:
        seen_pairs.add((m, j))
        major_jobs.append((m, j))

# =========================
# 7. UserJobPreference
# =========================
seen_pairs = set()
while len(user_job_prefs) < N_USER_JOB_PREF:
    u = random.choice(users)[0]
    j = random.choice(jobs)[0]
    if (u, j) not in seen_pairs:
        seen_pairs.add((u, j))
        user_job_prefs.append((u, j))

# =========================
# 8. UserMajorPreference
# =========================
seen_pairs = set()
while len(user_major_prefs) < N_USER_MAJOR_PREF:
    u = random.choice(users)[0]
    m = random.choice(majors)[0]
    if (u, m) not in seen_pairs:
        seen_pairs.add((u, m))
        user_major_prefs.append((u, m))

# =========================
# 9. Bookmark
# =========================
seen_pairs = set()
while len(bookmarks) < N_BOOKMARKS:
    u = random.choice(users)[0]
    p = random.choice(programs)[0]
    if (u, p) not in seen_pairs:
        seen_pairs.add((u, p))
        bookmarks.append((u, p))

# =========================
# 10. Comparison
# =========================
for i in range(1, N_COMPARISONS + 1):
    u = random.choice(users)[0]
    p1, p2 = random.sample(programs, 2)
    note = fake.sentence(nb_words=6)
    comparisons.append((i, u, p1[0], p2[0], note))

# =========================
# WRITE CSV HELPERS
# =========================
def write_csv(filename, header, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

# =========================
# WRITE ALL FILES
# =========================

# Major(MajorID, MajorName, Field)
write_csv(
    "Major.csv",
    ["MajorID", "MajorName", "Field"],
    majors,
)

# Job(JobID, JobTitle, Company, Location, AvgSalary)
write_csv(
    "Job.csv",
    ["JobID", "JobTitle", "Company", "Location", "AvgSalary"],
    jobs,
)

# University(UniversityID, Name, Location, Region, Tuition)
write_csv(
    "University.csv",
    ["UniversityID", "Name", "Location", "Region", "Tuition"],
    universities,
)

# Program(ProgramID, UniversityID, MajorID, MedianSalary, DegreeType)
write_csv(
    "Program.csv",
    ["ProgramID", "Name","UniversityID", "MajorID", "MedianSalary", "DegreeType"],
    programs,
)

# User(UserID, Username, Email, PasswordHash, PreferredMajor, PreferredLocation, PreferredJob)
write_csv(
    "User.csv",
    ["UserID", "Username", "Email", "PasswordHash", "PreferredMajor", "PreferredLocation", "PreferredJob"],
    users,
)

# MajorJob(MajorID, JobID)
write_csv(
    "MajorJob.csv",
    ["MajorID", "JobID"],
    major_jobs,
)

# UserJobPreference(UserID, JobID)
write_csv(
    "UserJobPreference.csv",
    ["UserID", "JobID"],
    user_job_prefs,
)

# UserMajorPreference(UserID, MajorID)
write_csv(
    "UserMajorPreference.csv",
    ["UserID", "MajorID"],
    user_major_prefs,
)

# Bookmark(UserID, ProgramID)
write_csv(
    "Bookmark.csv",
    ["UserID", "ProgramID"],
    bookmarks,
)

# Comparison(ComparisonID, UserID, ProgramID1, ProgramID2, NoteFromUser)
write_csv(
    "Comparison.csv",
    ["ComparisonID", "UserID", "ProgramID1", "ProgramID2", "NoteFromUser"],
    comparisons,
)

print("CSV files generated.")
