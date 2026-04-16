SELECT email
FROM bookmark
WHERE notify = 1
GROUP BY email;
