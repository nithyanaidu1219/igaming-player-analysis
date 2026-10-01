-- Top 10% by quarter GGR among all active bettors, rounded up.
-- Signed GGR includes player wins; its share can exceed 100% if other players have negative GGR.
WITH revenue AS (
 SELECT player_id,SUM(stakes_cents-payouts_cents) ggr FROM player_daily GROUP BY player_id
), ranked AS (
 SELECT *, ROW_NUMBER() OVER(ORDER BY ggr DESC,player_id) rn,COUNT(*) OVER() n FROM revenue
)
SELECT COUNT(*) active_bettors, SUM(CASE WHEN rn <= (n+9)/10 THEN 1 ELSE 0 END) top_players,
 SUM(ggr)/100.0 total_ggr_usd,
 SUM(CASE WHEN rn <= (n+9)/10 THEN ggr ELSE 0 END)/100.0 top_player_ggr_usd,
 ROUND(100.0*SUM(CASE WHEN rn <= (n+9)/10 THEN ggr ELSE 0 END)/NULLIF(SUM(ggr),0),2) top_ggr_share_pct
FROM ranked;
