/* Question 1 */
SELECT U.user_id, U.user_name , (U.review_count - U.fans) AS dif
FROM Users U
WHERE U.review_count > U.fans
  AND EXISTS (SELECT  1
              FROM Review R,Business B
              WHERE R.user_id= U.user_id
                AND B.business_id=R.business_id
                AND B.stars > 3.5)
ORDER BY dif DESC, user_id DESC ;


/* Question 2 */
SELECT U.user_name , B.business_name, T.date ,T.compliment_count
FROM Users U, Tip T, Business B
WHERE T.business_id=B.business_id
  AND T.user_id=U.user_id
  AND B.is_open= True
  AND T.compliment_count >2
  AND B.state ='TX'
ORDER BY T.compliment_count DESC, T.date DESC;


/* Question 3 */
SELECT U.user_name,COUNT(F.user_id2)
FROM Friend F,Users U
WHERE U.user_id=F.user_id1
GROUP BY (F.user_id1,U.user_name)
ORDER BY COUNT(F.user_id2) DESC ,U.user_name DESC
LIMIT 20;


/* Question 4 */
SELECT U.user_name , U.average_stars , U.yelping_since
FROM Users U
WHERE U.user_id IN (SELECT DISTINCT R.user_id
                    FROM Review R, Business B
                    WHERE B.business_id = R.business_id
                      AND R.stars < B.stars)
ORDER BY U.average_stars DESC ,U.yelping_since DESC;


/* Question 5*/
SELECT B.business_name, B.state , B.stars
FROM Business B
WHERE B.business_id IN (SELECT T.business_id
                        FROM Tip T
                        WHERE T.tip_text LIKE '%good%'
                          AND (SELECT EXTRACT(YEAR FROM T.date))=2020
                        GROUP BY T.business_id
                        HAVING COUNT(T.tip_text)= (SELECT Count(T1.tip_text)
                                                   FROM Tip T1
                                                   WHERE T1.tip_text LIKE '%good%'
                                                     AND (SELECT EXTRACT(YEAR FROM T1.date))=2020
                                                   GROUP BY T1.business_id
                                                   ORDER BY Count(T1.tip_text) DESC
                                                   LIMIT 1))
  AND B.is_open=True
ORDER BY B.stars DESC, B.business_name DESC;


/* Question 6*/
SELECT U1.user_name, U1.yelping_since, U1.average_stars
FROM Users U1, Friend F, Users U2
WHERE F.user_id2= U2.user_id
  AND F.user_id1= U1.user_id
GROUP BY U1.user_id
HAVING MIN(U2.average_stars)>U1.average_stars
ORDER BY U1.average_stars DESC, U1.yelping_since DESC;


/* Question 7 */
SELECT B.state,AVG(B.stars) AS avg_star
FROM Business B
GROUP BY (B.state)
ORDER BY avg_star DESC
LIMIT 10;


/* Question 8 */
SELECT tip_year , av_c
FROM (
SELECT Count(T.compliment_count) AS all_comp, (SELECT EXTRACT(YEAR FROM T.date))AS y_a, AVG(T.compliment_count) AS av_c
FROM Tip T
GROUP BY (SELECT EXTRACT(YEAR FROM T.date))) AS A
,(
SELECT Count(T.compliment_count) AS good_comp,(SELECT EXTRACT(YEAR FROM T.date)) tip_year
FROM Tip T
WHERE T.compliment_count>0
GROUP BY (SELECT EXTRACT(YEAR FROM T.date))) AS G
WHERE tip_year=y_a
  AND good_comp::DECIMAL/ all_comp::DECIMAL>0.01
ORDER BY tip_year ASC;


/* Question 9 */
SELECT U.user_name
FROM Users U
WHERE NOT EXISTS (SELECT DISTINCT R.review_id
                  FROM Review R, Business B
                  WHERE B.business_id = R.business_id
                    AND R.user_id = U.user_id
                    AND B.stars<=3.5)
ORDER BY U.user_name ASC;


/* Question 10*/
SELECT POPULAR.business_name , every_year.avg_star , every_year.year
FROM
(SELECT B.business_name ,R.business_id
FROM Business B, Review R
WHERE B.business_id=R.business_id
GROUP BY B.business_name ,R.business_id
HAVING COUNT (*)>1000) AS POPULAR,

(SELECT R1.business_id AS id, AVG(R1.stars) AS avg_star ,(SELECT EXTRACT(YEAR FROM R1.date)) AS year
FROM Review R1
GROUP BY R1.business_id,(SELECT EXTRACT(YEAR FROM R1.date))
HAVING AVG(R1.stars)>3 ) AS every_year
WHERE every_year.id=POPULAR.business_id
ORDER BY every_year.year ASC ,POPULAR.business_name ASC ;


/* Question 11 */
SELECT U.user_name, AGG.u , AGG.c, AGG.diff
FROM Users U,
(SELECT R.user_id , Sum(R.useful) As u , Sum(R.cool) As c , (Sum(R.useful)-Sum(R.cool)) As diff
FROM Review R
GROUP BY R.user_id) AS AGG
WHERE AGG.diff>0
  AND U.user_id=AGG.user_id
ORDER BY AGG.diff DESC, U.user_name DESC;


/* Question 12 */
SELECT DISTINCT F.user_id1,F.user_id2,R1.business_id,R1.stars
FROM  Review R1 , Review R2,((SELECT F2.user_id1 ,F2.user_id2
                                FROM Friend F1, Friend F2
                                WHERE F1.user_id1=F2.user_id2
                                  AND F1.user_id2=F2.user_id1
                                  AND F2.user_id1>F2.user_id2)
                               UNION
                               (SELECT *
                                FROM Friend F3
                                EXCEPT(SELECT F4.user_id1 ,F4.user_id2
                                       FROM Friend F4, Friend F5
                                       WHERE F4.user_id1=F5.user_id2
                                       AND F4.user_id2=F5.user_id1)))AS F
WHERE R1.user_id=F.user_id1
  AND R2.user_id=F.user_id2
  AND R2.business_id=R1.business_id
  AND R1.stars=R2.stars
ORDER BY R1.business_id DESC, R1.stars DESC;



/* Question 13 */
SELECT B.stars, B.state,COUNT(B.business_id)
FROM Business B
WHERE B.is_open=True
GROUP BY CUBE(B.stars, B.state);


/* Question 14*/
SELECT *
FROM  (SELECT U.user_id, U.review_count,U.fans,
                rank() OVER (PARTITION BY U.fans ORDER BY U.review_count DESC ) AS rank_number
         FROM  Users U
         WHERE U.fans>=50
           AND U.fans<=60
         ORDER BY rank_number) AS Ranked
WHERE Ranked.rank_number<=3
ORDER BY Ranked.rank_number ASC;
