-- Analyze how recovery chances relate to whether a customer broke a payment promise
SELECT 
  broken_promise_indicator,
  recovery_chance,
  COUNT(*) AS count
FROM Actions
GROUP BY broken_promise_indicator, recovery_chance
ORDER BY broken_promise_indicator;
