-- Days 0-6 after registration: equal seven-calendar-day observation windows.
-- Registrations after September 24 are excluded because data ends September 30.
WITH first_deposit AS (
 SELECT player_id, MIN(deposit_date) first_date FROM deposits GROUP BY player_id
)
SELECT substr(registration_date,1,7) registration_month,
 COUNT(*) eligible_registrations,
 SUM(CASE WHEN first_date < date(registration_date,'+7 days') THEN 1 ELSE 0 END) converted_7d,
 ROUND(100.0*SUM(CASE WHEN first_date < date(registration_date,'+7 days') THEN 1 ELSE 0 END)/COUNT(*),2) conversion_7d_pct
FROM players LEFT JOIN first_deposit USING(player_id)
WHERE registration_date <= '2026-09-24'
GROUP BY 1 ORDER BY 1;
