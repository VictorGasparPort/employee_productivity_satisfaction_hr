-- Query: Detecção de Anomalias Departamentais
SELECT 
    department,
    AVG(satisfaction_rate_percent) AS dept_avg,
    STDDEV(satisfaction_rate_percent) AS dept_stddev,
    COUNT(*) AS employees,
    (AVG(satisfaction_rate_percent) - (SELECT AVG(satisfaction_rate_percent) FROM main_table)) 
        / (SELECT STDDEV(satisfaction_rate_percent) FROM main_table) AS z_score
FROM main_table
GROUP BY department
HAVING ABS(AVG(satisfaction_rate_percent) - (SELECT AVG(satisfaction_rate_percent) FROM main_table)) 
    > 2 * (SELECT STDDEV(satisfaction_rate_percent) FROM main_table)
/* Objetivo: Identificar departamentos com satisfação estatisticamente anormal para investigação */