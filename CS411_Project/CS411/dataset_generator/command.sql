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

CREATE TABLE Program (
  ProgramID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(255),
  UniversityID INT,
  MajorID INT,
  MedianSalary INT,
  DegreeType VARCHAR(255),
  FOREIGN KEY (UniversityID) REFERENCES University(UniversityID),
  FOREIGN KEY (MajorID) REFERENCES Major(MajorID)
);

CREATE TABLE User (
  UserID INT AUTO_INCREMENT PRIMARY KEY,
  Username VARCHAR(255),
  Email VARCHAR(255),
  PasswordHash VARCHAR(255),
  PreferredMajor INT,
  PreferredLocation VARCHAR(255),
  PreferredJob INT,
  FOREIGN KEY (PreferredMajor) REFERENCES Major(MajorID),
  FOREIGN KEY (PreferredJob) REFERENCES Job(JobID)
);

CREATE TABLE Comparison (
  ComparisonID INT AUTO_INCREMENT PRIMARY KEY,
  UserID INT,
  ProgramID1 INT,
  ProgramID2 INT,
  NoteFromUser VARCHAR(255),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (ProgramID1) REFERENCES Program(ProgramID),
  FOREIGN KEY (ProgramID2) REFERENCES Program(ProgramID)
);

CREATE TABLE Bookmark(
    UserID INT,
    ProgramID INT,
    PRIMARY KEY(UserID, ProgramID),
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (ProgramID) REFERENCES Program(ProgramID)
);

CREATE TABLE MajorJob(
    MajorID INT,
    JobID INT,
    PRIMARY KEY(MajorID, JobID),
    FOREIGN KEY (MajorID) REFERENCES Major(MajorID),
    FOREIGN KEY (JobID) REFERENCES Job(JobID)
);

CREATE TABLE JobPreference(
    UserID INT,
    JobID INT,
    PRIMARY KEY(UserID, JobID),
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (JobID) REFERENCES Job(JobID)
);

CREATE TABLE MajorPreference(
    UserID INT,
    MajorID INT,
    PRIMARY KEY(UserID, MajorID),
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (MajorID) REFERENCES Major(MajorID)
);