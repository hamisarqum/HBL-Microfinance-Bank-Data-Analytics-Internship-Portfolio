-- Analyze how recovery chances vary by contact mode
SELECT 
  contact_mode,
  recovery_chance,
  COUNT(*) AS count
FROM Actions
GROUP BY contact_mode, recovery_chance
ORDER BY contact_mode, count DESC;
