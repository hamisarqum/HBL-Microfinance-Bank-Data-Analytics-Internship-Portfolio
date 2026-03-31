-- Analyze the distribution of customer contact modes used across all actions

SELECT 
  contact_mode,
  COUNT(*) AS count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Actions), 2) AS percentage
FROM Actions
GROUP BY contact_mode
ORDER BY count DESC;
