-- Find records with suspiciously short branch or distribution names
SELECT *
FROM Actions
WHERE LENGTH(branch_name) < 3 OR LENGTH(distribution_name) < 3;
