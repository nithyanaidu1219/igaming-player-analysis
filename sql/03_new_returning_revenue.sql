-- New = registered in the activity month; returning = registered earlier.
SELECT substr(activity_date,1,7) month,
 CASE WHEN substr(registration_date,1,7)=substr(activity_date,1,7)
 THEN 'New' ELSE 'Returning' END player_type,
 COUNT(DISTINCT player_id) active_bettors,
 SUM(stakes_cents-payouts_cents)/100.0 ggr_usd
FROM player_daily JOIN players USING(player_id)
GROUP BY 1,2 ORDER BY 1,2;
