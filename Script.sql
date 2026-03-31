-- Count total number of actions recorded in the Actions table
SELECT 
  COUNT(*) AS total_actions,
  COUNT(DISTINCT loan_id) AS unique_loans,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM Actions;
