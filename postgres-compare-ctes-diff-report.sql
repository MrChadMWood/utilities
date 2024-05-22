WITH table1 AS (
    SELECT True
) table2 AS (
    SELECT true
)
SELECT coalesce(t1.id, t2.id) AS id,
       CASE 
         WHEN t1.id IS NULL THEN 'Missing in table_1'
         WHEN t2.id IS NULL THEN 'Missing in table_2'
         ELSE 'At leASt one column is different'
       END AS status
FROM table_1 t1
FULL OUTER JOIN table_1 t2 ON t1.id = t2.id 
WHERE (t1 IS DISTINCT FROM t2)
   OR (t1.id IS NULL)
   OR (t2.id IS NULL);
