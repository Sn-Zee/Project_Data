--- first question
--- This query explores if there having 10 hours of study whilst being active in extracurricular activities have a positive impact in students' performance

SELECT
	hours_studied,
	AVG(exam_score) AS avg_exam_score
FROM student_performance
WHERE extracurricular_activities = 'Yes' AND hours_studied > 10
GROUP BY hours_studied
ORDER BY hours_studied DESC;

--- second quesiton
--- The query create bins to segregate data based on number of study time to have an insight if there's a range of study hours that is most effective to impact students' perfromance

SELECT
	CASE 
		WHEN hours_studied BETWEEN 1 AND 5 THEN '1-5 hours'
		WHEN hours_studied BETWEEN 6 AND 10 THEN '6-10 hours'
		WHEN hours_studied BETWEEN 11 AND 15 THEN '11-15 hours'
		ELSE '16+ hours' END AS hours_studied_range,
	AVG(exam_score) AS avg_exam_score
FROM student_performance
GROUP BY hours_studied_range
ORDER BY avg_exam_score DESC;


--- third question
--- Query shows rankings based on students' exam scores. Tied scores are ranked with the same number but does not skip any rank numbers

SELECT
	attendance,
	hours_studied,
	sleep_hours,
	tutoring_sessions,
	DENSE_RANK() OVER (ORDER BY exam_score DESC) AS exam_rank
FROM student_performance
LIMIT 30;