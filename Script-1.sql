-- Get the distribution of contact modes used in all actions
SELECT 
  contact_mode,
  COUNT(*) AS count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Actions), 2) AS percentage
FROM Actions
GROUP BY contact_mode
ORDER BY count DESC;


-- Recovery chance distribution
SELECT
    recovery_chance,
    COUNT(*) AS num_cases
FROM Actions
GROUP BY recovery_chance
ORDER BY num_cases DESC;

-- Branch-wise customer engagement
SELECT
    branch_name,
    COUNT(DISTINCT customer_id) AS customers_contacted,
    COUNT(*) AS total_actions
FROM Actions
GROUP BY branch_name
ORDER BY total_actions DESC;

-- Area-wise loan activity
SELECT
    area_name,
    COUNT(DISTINCT loan_id) AS unique_loans,
    COUNT(*) AS total_actions
FROM Actions
GROUP BY area_name
ORDER BY total_actions DESC;

-- Places where contact occurred
SELECT
    place_contacted,
    COUNT(*) AS contact_count
FROM Actions
GROUP BY place_contacted
ORDER BY contact_count DESC;

-- Account severity breakdown
SELECT
    account_severity,
    COUNT(*) AS total_cases
FROM Actions
GROUP BY account_severity
ORDER BY total_cases DESC;

-- Cross-tab: Severity vs Recovery Chance
SELECT
    account_severity,
    recovery_chance,
    COUNT(*) AS count
FROM Actions
GROUP BY account_severity, recovery_chance
ORDER BY account_severity, recovery_chance;

-- Total action amount by branch
SELECT
    branch_name,
    SUM(action_amount) AS total_action_amount
FROM Actions
GROUP BY branch_name
ORDER BY total_action_amount DESC;













