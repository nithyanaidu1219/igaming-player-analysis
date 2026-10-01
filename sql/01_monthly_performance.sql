-- SQLite dialect. Aggregate separate fact tables before joining to avoid multiplying money.
WITH months(month) AS (VALUES ('2026-07'),('2026-08'),('2026-09')),
a AS (
 SELECT substr(activity_date,1,7) month, COUNT(DISTINCT player_id) active_bettors,
        SUM(rounds) rounds, SUM(stakes_cents) stakes, SUM(payouts_cents) payouts
 FROM player_daily GROUP BY 1
), d AS (
 SELECT substr(deposit_date,1,7) month, COUNT(DISTINCT player_id) depositors,
        SUM(amount_cents) deposits FROM deposits GROUP BY 1
)
SELECT m.month, COALESCE(a.active_bettors,0) active_bettors,
 COALESCE(d.depositors,0) depositors, COALESCE(a.rounds,0) rounds,
 COALESCE(d.deposits,0)/100.0 deposits_usd,
 COALESCE(a.stakes,0)/100.0 stakes_usd, COALESCE(a.payouts,0)/100.0 payouts_usd,
 (COALESCE(a.stakes,0)-COALESCE(a.payouts,0))/100.0 ggr_usd,
 ROUND(100.0*(a.stakes-a.payouts)/NULLIF(a.stakes,0),2) ggr_margin_pct
FROM months m LEFT JOIN a USING(month) LEFT JOIN d USING(month) ORDER BY m.month;
