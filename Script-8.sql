-- Analyze financial metrics (action amounts) grouped by recovery chance
SELECT 
  recovery_chance,
  COUNT(*) AS total_actions,
  AVG(action_amount) AS avg_action_amount,
  MAX(action_amount) AS max_action_amount
FROM Actions
WHERE action_amount IS NOT NULL
GROUP BY recovery_chance
ORDER BY recovery_chance;
