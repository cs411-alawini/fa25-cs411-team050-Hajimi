USE cs411;


CREATE TABLE Major ( 
  MajorID INT AUTO_INCREMENT PRIMARY KEY,
  MajorName VARCHAR(255),
  Field VARCHAR(255)
);


CREATE TABLE Job (
  JobID INT AUTO_INCREMENT PRIMARY KEY,
  JobTitle VARCHAR(255),
  Company VARCHAR(255),
  Location VARCHAR(255),
  AvgSalary INT
);


CREATE TABLE University (
  UniversityID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(255),
  Location VARCHAR(255),
  Region VARCHAR(255),
  Tuition INT
);

-- Program table
-- Each program must have a valid UniversityID and MajorID
CREATE TABLE Program (
  ProgramID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(255),
  UniversityID INT NOT NULL,
  MajorID INT NOT NULL,
  MedianSalary INT,
  DegreeType VARCHAR(255),
  FOREIGN KEY (UniversityID) 
    REFERENCES University(UniversityID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (MajorID) 
    REFERENCES Major(MajorID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- User table
-- each user can have preferred major and job, but these are optional
CREATE TABLE User (
  UserID INT AUTO_INCREMENT PRIMARY KEY,
  Username VARCHAR(255),
  Email VARCHAR(255),
  PasswordHash VARCHAR(255),
  PreferredMajor INT NULL,
  PreferredLocation VARCHAR(255),
  PreferredJob INT NULL,
  FOREIGN KEY (PreferredMajor) 
    REFERENCES Major(MajorID)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  FOREIGN KEY (PreferredJob) 
    REFERENCES Job(JobID)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);

-- Comparison table
-- each comparison is made by exact one user comparing two programs
CREATE TABLE Comparison (
  ComparisonID INT AUTO_INCREMENT PRIMARY KEY,
  UserID INT NOT NULL,
  ProgramID1 INT NOT NULL,
  ProgramID2 INT NOT NULL,
  NoteFromUser VARCHAR(255),
  FOREIGN KEY (UserID) 
    REFERENCES User(UserID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (ProgramID1) 
    REFERENCES Program(ProgramID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  FOREIGN KEY (ProgramID2) 
    REFERENCES Program(ProgramID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Bookmark table
-- each user can bookmark many programs
-- each program can be bookmarked by many users
-- one bookmark must have valid UserID and ProgramID
CREATE TABLE Bookmark(
    UserID INT NOT NULL,
    ProgramID INT NOT NULL,
    PRIMARY KEY(UserID, ProgramID),
    FOREIGN KEY (UserID) 
      REFERENCES User(UserID)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
    FOREIGN KEY (ProgramID) 
      REFERENCES Program(ProgramID)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

-- Major-Job table
-- a major can be related to many jobs
-- a job can be related to many majors
CREATE TABLE MajorJob(
    MajorID INT NOT NULL,
    JobID INT NOT NULL,
    PRIMARY KEY(MajorID, JobID),
    FOREIGN KEY (MajorID) 
      REFERENCES Major(MajorID)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
    FOREIGN KEY (JobID) 
      REFERENCES Job(JobID)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

-- User preferences tables
-- each user can have many preferred jobs
-- each job can be preferred by many users
CREATE TABLE JobPreference(
    UserID INT NOT NULL,
    JobID INT NOT NULL,
    PRIMARY KEY(UserID, JobID),
    FOREIGN KEY (UserID) 
      REFERENCES User(UserID)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
    FOREIGN KEY (JobID) 
      REFERENCES Job(JobID)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

-- major-preference table
-- each user can have many preferred majors
-- each major can be preferred by many users
CREATE TABLE MajorPreference(
    UserID INT NOT NULL,
    MajorID INT NOT NULL,
    PRIMARY KEY(UserID, MajorID),
    FOREIGN KEY (UserID) 
      REFERENCES User(UserID)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
    FOREIGN KEY (MajorID) 
      REFERENCES Major(MajorID)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);