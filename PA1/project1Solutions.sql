Q1
Select DISTINCT U.user_id, U.name, (U.review_count - U.fans) as diff
From Users U, Review R, Business B
Where U.user_id = R.user_id and B.business_id = R.business_id and B.stars > 3.5 and U.review_count > U.fans
Order By diff, user_id DESC;

Q2
Select U.name, B.name, T.date, T.compliment_count 
From Business B, Tip T, Users U
Where B.business_id = T.business_id and B.is_open = TRUE and B.state = 'TX' and U.user_id = T.user_id and T.compliment_count > 2
Order By T.compliment_count, T.date DESC;

Q3
Select DISTINCT F.user_id1, FriendCount.counts
From (Select F.user_id1, Count(*) as counts
From Friend F
Group By F.user_id1) as FriendCount, Friend F, Users U
Where F.user_id1 = FriendCount.user_id1
Order By FriendCount.counts, F.name DESC
LIMIT 20;

Q4
Select U1.name, U1.average_stars, U1.yelping_since
From Users U1 
Where U1.user_id IN (
Select DISTINCT U.user_id
From Review R, Users U, Business B
Where R.user_id = U.user_id and R.business_id = B.business_id and R.stars < B.stars)
Order By U1.average_stars, U1.yelping_since;

Q5
Select B.name, B.state, B.stars
From Business B, (Select B.business_id, Count(*) as counts
From Business B, Tip T 
Where B.business_id = T.business_id and T.date > '2019-12-31'::date and T.tip_text LIKE '%good%' 
Group By B.business_id) as GoodTips
Where GoodTips.counts >= ALL (Select Count(*) as counts
From Business B, Tip T 
Where B.business_id = T.business_id and T.date > '2019-12-31'::date and T.tip_text LIKE '%good%' 
Group By B.business_id) and GoodTips.business_id = B.business_id
Order By B.stars, B.name DESC;

Q6
Select U.name, U.average_stars, U1.yelping_since
From Users U, Friend F, Users U2
Where U.user_id = F.user_id1 and U2.user_id = F.user_id2
Group By U.user_id
HAVING MIN(U2.average_stars) > U.average_stars
Order By U1.average_stars, U1.yelping_since;

Q7
Select B.state, AVG(B.stars) as avg_stars
From Business B
Group By B.state
Order By avg_stars DESC
LIMIT 10;

Q8
Select GoodYears.year, AVG(allYears.allCount)
From (Select date_trunc('year', date) as year,Count(*) as goodCount 
	From Tip T 
	Where T.compliment_count > 0 Group By year) as GoodYears, 
	(Select date_trunc('year', date) as year, Count(*) as allCount From Tip T Group by year) as allYears 
Where GoodYears.year = allYears.year and GoodYears.goodCount > 1*allYears.allCount/100
Group BY GoodYears.year;

Q9
Select U.name
From (Select U2.user_id, Count(*) as counts
	From Users U2, Review R
	Where R.user_id = U2.user_id Group By U2.user_id) as allRate,
	(Select U.user_id, Count(*) as counts
	From Users U, Review R, Business B
	Where U.user_id = R.user_id and R.business_id = B.business_id and B.stars > 3.5 Group By U.user_id) as highRate, Users U
Where allRate.user_id = highRate.user_id and allRate.counts = highRate.counts and U.user_id = allRate.user_id

Q10
Select B.name, Res.avg_stars, Res.year
From (Select PopularBusinesses.business_id, AVG(PopularBusinesses.stars) as avg_stars, date_trunc('year', date) as year
From (Select B.business_id, B.stars
From Business B, Review R
Where R.business_id = B.business_id
Group By B.business_id
HAVING Count(*) > 1000) as PopularBusinesses, Review R
Where PopularBusinesses.business_id = R.business_id
Group By PopularBusinesses.business_id, year
Having AVG(PopularBusinesses.stars) > 3) as Res, Business B
Where B.business_id = Res.business_id
Order By Res.year ASC;

Q11
Select U.name, coolsFuns.usefuls, coolsFuns.cools, (coolsFuns.usefuls - coolsFuns.cools) as diff
From Users U, (Select R.user_id, sum(r.useful) as usefuls sum(r.cool) as cools
From Review R
Group By R.user_id
HAVING usefuls > cools
) as coolsFuns
Where coolsFuns.user_id = U.user_id
Order By diff, name DESC;


Q12
Select B.business_id, U.user_id, U2.user_id, R.stars
From Users U, Users U2, Friend F, Business B, Review R, Review R2
Where F.user_id1 < F.user_id2 and F.user_id1 = R.user_id and F.user_id2=R2.user_id 
and F.user_id1 = U.user_id and F.user_id2 = U2.user_id and R.business_id = R2.business_id 
and R.business_id = B.business_id and R.stars = R2.stars
Order By B.business_id, R.stars DESC;

Q13
SELECT B.stars, B.state, Count(*)
FROM Business B
Where B.is_open = TRUE
GROUP BY CUBE (stars, state);

Q14
SELECT * FROM (
SELECT user_id, review_count, fans,
rank() OVER ( PARTITION BY fans ORDER BY review_count DESC )
FROM Users
WHERE fans BETWEEN 50 AND 60
) as X
WHERE rank <= 3;