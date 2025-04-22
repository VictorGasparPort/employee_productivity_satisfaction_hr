-- Query : Risco de Rotatividade (Identifica potenciais demissões)
WITH RiskFactors AS (
    /* CTE: Combina múltiplos indicadores de insatisfação */
    SELECT 
        name,
        CASE 
            WHEN satisfaction_rate_percent < 60 THEN 3
            WHEN feedback_score < 3 THEN 2
            WHEN productivity_percent < department_avg THEN 1
            ELSE 0
        END AS risk_score,
        PERCENT_RANK() OVER (ORDER BY salary) AS salary_percentile
    FROM (
        SELECT *,
            AVG(productivity_percent) OVER (PARTITION BY department) AS department_avg
        FROM main_table
    ) sub
)
SELECT 
    department,
    COUNT(*) FILTER (WHERE risk_score >= 2) AS high_risk_employees,
    AVG(salary_percentile) AS avg_salary_position
FROM RiskFactors
GROUP BY department
HAVING COUNT(*) FILTER (WHERE risk_score >= 2) > 3
/* Objetivo: Priorizar departamentos com maior risco de turnover para ações de retenção */