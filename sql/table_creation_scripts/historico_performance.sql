-- Tabela: Histórico de Performance (Armazena métricas consolidadas por trimestre)
CREATE TABLE employee_performance_history AS
/* Propósito: Permitir análise temporal de performance sem recalcular dados brutos */
SELECT 
    name,
    department,
    EXTRACT(YEAR FROM joining_date) AS year,
    CASE 
        WHEN EXTRACT(MONTH FROM joining_date) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN EXTRACT(MONTH FROM joining_date) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN EXTRACT(MONTH FROM joining_date) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    AVG(productivity_percent) OVER (PARTITION BY department ORDER BY joining_date 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS rolling_avg_productivity,
    COUNT(projects_completed) AS total_projects
FROM main_table
GROUP BY name, department, year, quarter;
