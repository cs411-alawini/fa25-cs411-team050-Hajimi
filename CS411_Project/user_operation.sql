-- 1. Browse & search programs
-- 1.1 search programs by major and location
-- input: major, location
-- output: list of programs matching the criteria
SELECT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName, u.Location,
       m.MajorName, p.DegreeType, p.MedianSalary
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
JOIN Major m      ON p.MajorID = m.MajorID
WHERE m.MajorName = Major_input
  AND u.Location = Location_input;

-----------------------------------------------------------------------------------------------------------------
-- 1.2 Filter programs by tuition and salary
-- input: max_tuition, min_salary
-- output: list of programs within the tuition and salary range
SELECT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName, u.Tuition,
       p.MedianSalary
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
WHERE u.Tuition < Max_Tuition_input
  AND p.MedianSalary > Min_Salary_input
ORDER BY p.MedianSalary DESC;

-----------------------------------------------------------------------------------------------------------------
-- 1.3 list all programs for a given university
-- input: university_name
-- output: list of programs offered by the university
SELECT p.ProgramID, p.Name AS ProgramName,
       m.MajorName, p.DegreeType, p.MedianSalary
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
JOIN Major m      ON p.MajorID = m.MajorID
WHERE u.Name = University_Name_input
Order by p.ProgramID;

-----------------------------------------------------------------------------------------------------------------
-- 1.4 View Program details, including related jobs
-- input: program_id
-- output: program details and related job listings
SELECT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName, u.Location,
       m.MajorName, m.Field,
       j.JobID, j.JobTitle, j.Company, j.Location AS JobLocation, j.AvgSalary
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
JOIN Major m      ON p.MajorID = m.MajorID
JOIN MajorJob mj  ON m.MajorID = mj.MajorID
JOIN Job j        ON mj.JobID = j.JobID
WHERE p.ProgramID = Program_ID_input;  -- program user is viewing
-----------------------------------------------------------------------------------------------------------------

-- 2. Majors <-> Jobs exploration
-- 2.1 Jobs related to a major
-- input: major_name
-- output: list of jobs related to the major
SELECT j.JobID, j.JobTitle, j.Company, j.Location, j.AvgSalary
FROM Major m
JOIN MajorJob mj ON m.MajorID = mj.MajorID
JOIN Job j       ON mj.JobID = j.JobID
WHERE m.MajorName = Major_Name_input;
-----------------------------------------------------------------------------------------------------------------
-- 2.2 Major that lead to a job
-- input: job_title
-- output: list of majors that can lead to the job
SELECT DISTINCT m.MajorID, m.MajorName, m.Field
FROM Job j
JOIN MajorJob mj ON j.JobID = mj.JobID
JOIN Major m     ON mj.MajorID = m.MajorID
WHERE j.JobTitle = Job_Title_input;
-----------------------------------------------------------------------------------------------------------------
-- 2.3 10 top-paying jobs for one major
-- input: major_name
-- output: list of top 10 highest paying jobs for the major
SELECT 
    j.JobID,
    j.JobTitle,
    j.Company,
    j.Location,
    j.AvgSalary
FROM Major m
JOIN MajorJob mj ON m.MajorID = mj.MajorID
JOIN Job j       ON mj.JobID = j.JobID
WHERE m.MajorName = Major_Name_input
ORDER BY j.AvgSalary DESC
LIMIT 10;
------------------------------------------------------------------------------------------------------------------
-- 3. User preferences & personalization
-- 3.1 set user's preferred major and job
-- input: user_id, preferred_major_id, preferred_job_id
UPDATE `User`
SET PreferredMajor = Major_ID_input,
    PreferredJob   = Job_ID_input
WHERE UserID = User_ID_input;
-----------------------------------------------------------------------------------------------------------------
-- 3.2 add a user's multiple preferred majors
-- input: user_id, preferred_major_id
INSERT INTO UserPreferredMajors (UserID, MajorID)
VALUES (User_ID_input, Major_ID_input);
-----------------------------------------------------------------------------------------------------------------
-- 3.3 add multiple preferred jobs
-- input: user_id, preferred_job_id
INSERT INTO UserPreferredJobs (UserID, JobID)
VALUES (User_ID_input, Job_ID_input);
-----------------------------------------------------------------------------------------------------------------
-- 3.4 Get all of a user's preferred majors and jobs
-- input: user_id
-- Preferred majors
SELECT m.MajorID, m.MajorName, m.Field
FROM MajorPreference mp
JOIN Major m ON mp.MajorID = m.MajorID
WHERE mp.UserID = User_ID_input;

-- Preferred jobs
SELECT j.JobID, j.JobTitle, j.Company, j.AvgSalary
FROM JobPreference jp
JOIN Job j ON jp.JobID = j.JobID
WHERE jp.UserID = User_ID_input;
------------------------------------------------------------------------------------------------------------------
-- 3.5 delete a user's preferred major
-- input: user_id, preferred_major_id
DELETE FROM UserPreferredMajors
WHERE UserID = User_ID_input
  AND MajorID = Major_ID_input;

------------------------------------------------------------------------------------------------------------------
-- 3.6 delete a user's preferred job
-- input: user_id, preferred_job_id
DELETE FROM UserPreferredJobs
WHERE UserID = User_ID_input
  AND JobID = Job_ID_input;

------------------------------------------------------------------------------------------------------------------
-- 3.7 Recommend programs based on user's preferred major and location
-- input: user_id
SELECT DISTINCT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName, u.Location,
       m.MajorName, p.MedianSalary
FROM `User` us
JOIN MajorPreference mp ON us.UserID = mp.UserID
JOIN Program p          ON mp.MajorID = p.MajorID
JOIN University u       ON p.UniversityID = u.UniversityID
JOIN Major m            ON p.MajorID = m.MajorID
WHERE us.UserID = User_ID_input
  AND (us.PreferredLocation IS NULL OR u.Location = us.PreferredLocation)
ORDER BY p.MedianSalary DESC;

------------------------------------------------------------------------------------------------------------------
-- 4. Bookmarks
-- 4.1 Add a program to user's bookmarks
-- input: user_id, program_id
INSERT INTO Bookmark (UserID, ProgramID)
VALUES (User_ID_input, Program_ID_input);
------------------------------------------------------------------------------------------------------------------
-- 4.2 Remove a program from user's bookmarks
-- input: user_id, program_id
DELETE FROM Bookmark
WHERE UserID = User_ID_input
  AND ProgramID = Program_ID_input;
------------------------------------------------------------------------------------------------------------------
-- 4.3 Get all bookmarked programs for a user
-- input: user_id
SELECT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName, m.MajorName,
       p.DegreeType, p.MedianSalary
FROM Bookmark b
JOIN Program p    ON b.ProgramID = p.ProgramID
JOIN University u ON p.UniversityID = u.UniversityID
JOIN Major m      ON p.MajorID = m.MajorID
WHERE b.UserID = User_ID_input;
------------------------------------------------------------------------------------------------------------------
-- 4.4 Find most-bookmarked programs
-- output: list of programs with the highest number of bookmarks
SELECT p.ProgramID, p.Name AS ProgramName,
       u.Name AS UniversityName,
       COUNT(*) AS BookmarkCount
FROM Bookmark b
JOIN Program p    ON b.ProgramID = p.ProgramID
JOIN University u ON p.UniversityID = u.UniversityID
GROUP BY p.ProgramID, p.Name, u.Name
ORDER BY BookmarkCount DESC
LIMIT 10;

------------------------------------------------------------------------------------------------------------------
-- 5. Comparisons
-- 5.1 create a comparison between two programs
-- input: user_id, program_id_1, program_id_2, note
INSERT INTO Comparison (UserID, ProgramID1, ProgramID2, Note)
VALUES (User_ID_input, Program_ID_1_input, Program_ID_2_input, Note_input);
------------------------------------------------------------------------------------------------------------------
-- 5.2 show all comparisons made by a suer with program details
-- input: user_id
SELECT c.ComparisonID,
       p1.ProgramID AS Program1ID,
       p1.Name      AS Program1Name,
       u1.Name      AS Univ1Name,
       p2.ProgramID AS Program2ID,
       p2.Name      AS Program2Name,
       u2.Name      AS Univ2Name,
       c.NoteFromUser
FROM Comparison c
JOIN Program p1 ON c.ProgramID1 = p1.ProgramID
JOIN University u1 ON p1.UniversityID = u1.UniversityID
JOIN Program p2 ON c.ProgramID2 = p2.ProgramID
JOIN University u2 ON p2.UniversityID = u2.UniversityID
WHERE c.UserID = User_ID_input
ORDER BY c.ComparisonID DESC;
------------------------------------------------------------------------------------------------------------------
-- 5.3 Find the most frequently compared programs
SELECT prog.ProgramID, prog.Name AS ProgramName,
       u.Name AS UniversityName,
       COUNT(*) AS TimesCompared
FROM (
    SELECT ProgramID1 AS ProgramID FROM Comparison
    UNION ALL
    SELECT ProgramID2 AS ProgramID FROM Comparison
) AS all_prog
JOIN Program prog   ON all_prog.ProgramID = prog.ProgramID
JOIN University u   ON prog.UniversityID = u.UniversityID
GROUP BY prog.ProgramID, prog.Name, u.Name
ORDER BY TimesCompared DESC
LIMIT 10;
------------------------------------------------------------------------------------------------------------------
-- 6. Analytics
-- 6.1 Average salary by major
SELECT m.MajorName, AVG(p.MedianSalary) AS AvgMedianSalary
FROM Major m
JOIN Program p ON m.MajorID = p.MajorID
GROUP BY m.MajorName
ORDER BY AvgMedianSalary DESC;
------------------------------------------------------------------------------------------------------------------
-- 6.2 Count of programs by university and degree type
SELECT u.Name AS UniversityName,
       p.DegreeType,
       COUNT(*) AS NumPrograms
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
GROUP BY u.Name, p.DegreeType
ORDER BY u.Name, p.DegreeType;
------------------------------------------------------------------------------------------------------------------
-- 6.3 Average tuition and salary by region
SELECT u.Region,
       AVG(u.Tuition)      AS AvgTuition,
       AVG(p.MedianSalary) AS AvgMedianSalary
FROM University u
JOIN Program p ON u.UniversityID = p.UniversityID
GROUP BY u.Region
ORDER BY AvgMedianSalary DESC;
------------------------------------------------------------------------------------------------------------------