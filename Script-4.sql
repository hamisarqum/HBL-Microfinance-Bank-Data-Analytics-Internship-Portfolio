-- Analyze the number of actions per branch, segmented by recovery chance
SELECT 
  branch_name,
  recovery_chance,
  COUNT(*) AS count
FROM Actions
GROUP BY branch_name, recovery_chance
ORDER BY branch_name, count DESC;
