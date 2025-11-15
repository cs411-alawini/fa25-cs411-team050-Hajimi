-- Q1: Top bookmarked programs by field
SELECT 
    a.ProgramID,
    a.ProgramName,
    a.Field,
    a.bookmark_count
FROM (
    SELECT 
        p.ProgramID,
        p.Name AS ProgramName,
        m.Field,
        COUNT(*) AS bookmark_count
    FROM Bookmark b
    JOIN Program p ON b.ProgramID = p.ProgramID
    JOIN Major m ON p.MajorID = m.MajorID
    GROUP BY p.ProgramID, p.Name, m.Field
) AS a
WHERE (
    SELECT COUNT(*)
    FROM (
        SELECT 
            p2.ProgramID,
            p2.Name AS ProgramName,
            m2.Field,
            COUNT(*) AS bookmark_count
        FROM Bookmark b2
        JOIN Program p2 ON b2.ProgramID = p2.ProgramID
        JOIN Major m2 ON p2.MajorID = m2.MajorID
        GROUP BY p2.ProgramID, p2.Name, m2.Field
    ) AS b
    WHERE b.Field = a.Field 
      AND b.bookmark_count > a.bookmark_count
) < 15
ORDER BY a.Field, a.bookmark_count DESC;



------------------------------------------------------------------------------------------------------------------
-- Q2: Universities that have been compared the most frequently
SELECT
    LEAST(u1.Name, u2.Name) AS UnivA,
    GREATEST(u1.Name, u2.Name) AS UnivB,
    COUNT(*) AS times_compared
FROM Comparison c
JOIN Program p1 ON c.ProgramID1 = p1.ProgramID
JOIN University u1 ON p1.UniversityID = u1.UniversityID
JOIN Program p2 ON c.ProgramID2 = p2.ProgramID
JOIN University u2 ON p2.UniversityID = u2.UniversityID
GROUP BY LEAST(u1.Name, u2.Name), GREATEST(u1.Name, u2.Name)
HAVING COUNT(*) >= 1
ORDER BY times_compared DESC
LIMIT 15;


-----------------------------------------------------------------------------------------------------------------
--Q3: Top median salary by major
SELECT 
    m.MajorName,
    m.Field,
    p.Name AS ProgramName,
    ROUND(AVG(p.MedianSalary), 2) AS Avg_Median_Salary
FROM Program p
JOIN Major m ON p.MajorID = m.MajorID
GROUP BY m.MajorID, m.MajorName, m.Field, p.Name
ORDER BY Avg_Median_Salary DESC
LIMIT 15;



-----------------------------------------------------------------------------------------------------------------
--Q4: Program that has high tuition but low median salary
SELECT
    p.Name AS ProgramName,
    u.Name AS University,
    m.MajorName,
    m.Field,
    p.ProgramID,
    p.DegreeType,
    u.Tuition,
    p.MedianSalary,
    ROUND(p.MedianSalary - u.Tuition, 2) AS ValueScore
FROM Program p
JOIN University u ON p.UniversityID = u.UniversityID
JOIN Major m ON p.MajorID = m.MajorID
WHERE p.MedianSalary IS NOT NULL
  AND u.Tuition > (SELECT AVG(Tuition) FROM University)
ORDER BY ValueScore ASC
LIMIT 15;



-----------------------------------------------------------------------------------------------------------------
--remove carriage returns

UPDATE `Comparison` SET `NoteFromUser` = REPLACE(`NoteFromUser`, '\r', '');   
UPDATE `Job` SET `JobTitle` = REPLACE(`JobTitle`, '\r', '');                  
UPDATE `Job` SET `Company` = REPLACE(`Company`, '\r', '');                    
UPDATE `Job` SET `Location` = REPLACE(`Location`, '\r', '');                  
UPDATE `Major` SET `MajorName` = REPLACE(`MajorName`, '\r', '');              
UPDATE `Major` SET `Field` = REPLACE(`Field`, '\r', '');                      
UPDATE `Program` SET `DegreeType` = REPLACE(`DegreeType`, '\r', '');
UPDATE `Program` SET `Name` = REPLACE(`Name`, '\r', '');
UPDATE `University` SET `Name` = REPLACE(`Name`, '\r', '');                   
UPDATE `University` SET `Location` = REPLACE(`Location`, '\r', '');           
UPDATE `University` SET `Region` = REPLACE(`Region`, '\r', '');               
UPDATE `User` SET `Username` = REPLACE(`Username`, '\r', '');                 
UPDATE `User` SET `Email` = REPLACE(`Email`, '\r', '');                       
UPDATE `User` SET `PasswordHash` = REPLACE(`PasswordHash`, '\r', '');         
UPDATE `User` SET `PreferredLocation` = REPLACE(`PreferredLocation`, '\r', '');