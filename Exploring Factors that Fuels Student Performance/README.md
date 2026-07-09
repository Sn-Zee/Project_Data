# Analysis on Student Peformance using SQL

## Project Overview

This project explores the student performance data to determine the factors that influence student academic performance using SQL. By analyzing attendance, study habits, sleep patterns, tutoring sessions, extracurricular activities, and teacher quality. The project aims to identify which factors have the greatest impact on the performance based on final exam scores.

The objective of this is to demonstrate SQL skills through data exploration, aggregation, filtering, and analytical queries while generating meaningful educational insightqs that could support a data-driven decision making for educators and institutions.

## Objectives

- Analyze Student Performance data using SQL
- Identify factors associated with higher exam scores
- Compare academic performance across different student groups
- Demonstrate SQL querying techniques includeing:
    * Filtering
    * Aggregation
    * GROUP BY
    * CASE Statements
    * ORDER BY
    * Conditional Analysis
    * Window Functions

## Dataset

| Column | Definition | Datatype |
| ------ | ---------- | -------- |
| `attendace` | Percentage of classes attended | `float` |
| `extracirricular_activities` | Participation in extracurricular activities | `varchar` (Yes, No) |
| `sleep hours` | Average number of hours of sleep per night | `float` |
| `tutoring_sessions` | Number of tutoring sessions attended per month | `integer` |
| `teacher_quality` | Quality of the teachers | `varchar` (Low, Medium, High) |
| `exam_score` | Final exam score | `float` |

## Technologies Used

- SQL
- PostgreSQL

## SQL Skills Demonstrated

- GROUP BY
- ORDER BY
- AVG()
- COUNT()
- Aggregation Functions
- CASE
- Filtering
- Sorting
- Window Functions

## Questions Answered

1. Do more study hours and extracurricular activities lead to better scores? (Analyze how studying more than 10 hours per week, while participating in extracurricular activities impact performance)
2. How many study hours is the most effective? (Explore how different ranges of study hours impact exam performance)
3. Show relative ranks of the students without revealing the respective exam scores. (Ranks are based on exam score, ensuring that students with the same exam score should share the same rank and no ranks are skipped)

## Key Insights

1. Among students who participates in extracurricular activities and study more than 10 hours per week, those who studiend 43 hours achieved the highest average exam score of 78. Although there are minor fluctuations in the average exam scores across different study hours, the overall trend suggests that students who spend more time studying tend to achieve higher average exam scores within this group.

2. Students who studied 16 or more hours per week achieved the highest average exam score (67.92) among all study-hour groups identified. The analysis indicates a positive relationship between study time and exam performance, with average exam scores are increasing as weekly study hours increases. This suggests that putting more time to study is associated with a better academic performance.

3. Among the top 30 students ranked by exam score, study hours rangef from 11 to 31 hours per week, attendance from 62% to 99%, sleep duration varied between 4 and 9 hours, and tutoring sessions ranged from 0 to 5 per month. These results suggests that high academic performance is associated withh a combination of factors. Additionally, highest ranked student attended five tutoring sessions, the highest number recorded within this group.

 While the top student attended five tutoring sessions, several top performing students attended fewer or no tutoring sessions. To further examine the relationship between tutoring and academic performance, an additional analysis was conducted by comparing the average exam scores across different number of tutoring sessions for the entire dataset. The result indicate that students who attends more tutoring sessions generally achieves higher average exam scores, suggesting a positive association between tutoring attendance and academic performance.

## Future Improvements

1. Analyze additional factors such as attendance, sleep hours, and  teacher quality.
2. Dataset can be expanded including additional factors that may influence performance such as school type, parent academic level, internet access, etc.
3.  Develop an interactive dashboard or a dashboard using visualization tools that enables user to explore the data.