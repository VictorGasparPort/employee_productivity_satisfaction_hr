
-- Query: Turnover por Tempo de Casa (Análise de Retenção)
/* Propósito: Identificar padrões de saída baseado na experiência */
SELECT 
    CASE 
        WHEN DATE_PART('year', CURRENT_DATE - joining_date) < 2 THEN 'Junior (0-2 anos)'
        WHEN DATE_PART('year', CURRENT_DATE - joining_date) BETWEEN 2 AND 5 THEN 'Mid (2-5 anos)'
        ELSE 'Senior (5+ anos)'
    END AS experience_group,
    COUNT(*) AS total_employees,
    COUNT(*) FILTER (WHERE satisfaction_rate_percent < 50) AS dissatisfied
FROM main_table
GROUP BY 1
ORDER BY MIN(DATE_PART('year', CURRENT_DATE - joining_date));