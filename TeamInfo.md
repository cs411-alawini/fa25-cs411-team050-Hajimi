# team050-Hajimi

## Basic Information

|   Info      |        Description     |
| ----------- | ---------------------- |
| TeamID      |        Team-050        |
| TeamName    |         Hajimi         |
| Captain     |       Wenhao Zhang     |
| Captain     |  wenhaoz5@illinois.edu |
| Member1     |        Yuhui Liu       |
| Member1     |   yuhuil4@illinois.edu |
| Member2     |     Tianxiang Wu       |
| Member2     |  tw50@illinois.edu     |
| Member3     |       Zixuan Huang     |
| Member3     | zixuan23@illinois.edu  |

## Project Information

|   Info      |        Description                                    |
| ----------- | ----------------------------------------------------- |
|  Title      |      College Employment & Salary Analysis Platform    |
| System URL  |      link_to_system                                   |
| Video Link  |      link_to_video                                    |

## Project Summary
Choosing a college major and university is one of the most significant financial and career decisions for students and their families. However, current resources often emphasize prestige-based rankings (such as US News) rather than concrete outcomes like employment rates and post-graduation salaries. In our project, we will address this problem by building a web-based analysis platform that integrates the real world datasets: the U.S. Department of Education’s College Scorecard (covering tuition, majors, and alumni salaries) with job and salary data from Kaggle/Glassdoor.

This platform will allow users to  explore how different majors and universities compare in terms of the salary. For instance, a student can search for “Computer Science” graduates at Illinois, compare their average salary with similar programs at MIT or Purdue, and weigh the results against tuition costs. 

#### Detailed description:
Our platform aims to solve the problem of informed college decision-making. Currently, families face uncertainty when evaluating if the cost of a college degree will truly “pay off” in the long run. By comparing educational cost and graduate outcomes, our platform will help answer the key question listed below:
What are the typical salaries for graduates in a specific field?
Which universities deliver the best ROI(return of investment) for a given major?
 How do different institutions compare regionally or nationally?

#### Usefulness:
Our project will be useful for high school students, parents and counselors who want a more practical tool when evaluating the university. Instead of using the prestige, the user can directly see outcome-based evidence for their decisions. While similar websites do exist like the College Scoreboard official website, they often present raw data and the format is difficult to follow for users. Our project is totally different since it integrates multiple datasets, not just one. Moreover, it will focus on ROI(Return of Investment) and employment outcomes instead of general rankings.

#### Realness:
We will use real, publicly available datasets:
U.S. Department of Education- College ScoreBoard
		Size:Thousands of universities and programs across the U.S.
		Content: Tuition, graduation rate, debt levels, alumni median earnings, majors offered.
Job/Salary Data from Kaggle or Glassdoor:
		Size:At least 50,000+ job postings/salary entries.
		Content: Company names, job roles, average salaries, location.

By combining these datasets, we can cross-reference educational inputs (tuition, degree field) with career outcomes (job market salary averages). Each dataset is sufficiently large (≥1K records per table), ensuring we can meet project requirements.

#### Functionality:
1.Search&View: Users can search for a university or major and view salary/employment outcomes.
2.Compare: Users can select multiple universities or majors for side-by-side ROI comparison.
3.Filter: Users can filter results by region, tuition range, or field of study.
4. User Accounts: Students can create accounts, save comparisons, and bookmark schools/majors.
	Create: Users create accounts, save comparisons, bookmark universities.
	Read: Browse/search/filter universities and majors.
	Update: Users update their saved comparisons or account info.
	Delete: Users delete saved comparisons or bookmarks.
	To be continue……..

#### Low-Fidelity UI Mockup:
**Homepage:** The homepage provides a search bar at the top where users can type a school or major. A filter button on the left expands to reveal advanced filtering options, including school name, major, and salary range (min–max). A search button on the right executes the query. This page is the main entry point for users to begin exploring universities and majors.

**University / Major Detail Page:** This page displays detailed statistics for a specific school and major, including tuition, graduation rate, and median salary. A visualization chart (e.g., histogram or distribution plot) shows salary levels with interactive hover functionality to view percentages. At the top, users can navigate back to the homepage or select the program to add to a comparison. This page helps users see in-depth information for one program at a time.

**Comparison Dashboard:** The comparison page allows users to select two schools/majors side by side. For each program, tuition, graduation rate, and salary data are shown in a structured column layout. Simple charts below provide quick visual comparisons. A button at the top lets users save the comparison to their account for future reference, a navigation button goes to the comparison board, and another navigation button returns to the homepage. This page emphasizes ROI comparison across institutions.

###### User Account Page
**Bookmarks & Saved Comparisons:** Users can view saved schools, majors, or comparisons. Each entry lists details (school, major, salary, grad rate) with delete buttons on the right for removing items.
**Account Settings:** Users can edit personal details such as username, email, preferred school/major, and job interests.



