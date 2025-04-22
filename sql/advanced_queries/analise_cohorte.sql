-- Query: Análise de Cohorte por Contratação
SELECT 
    EXTRACT(YEAR FROM joining_date) AS cohort_year,
    department,
    ROUND(AVG(productivity_percent), 2) AS year_1_productivity,
    ROUND((LEAD(AVG(productivity_percent)) OVER (PARTITION BY department ORDER BY EXTRACT(YEAR FROM joining_date)), 2) AS year_2_productivity,
    ROUND(((LEAD(AVG(productivity_percent)) OVER (PARTITION BY department ORDER BY EXTRACT(YEAR FROM joining_date)) - 
        AVG(productivity_percent)) / AVG(productivity_percent) * 100, 2) AS productivity_growth
FROM main_table
GROUP BY 1,2
/* Propósito: Medir crescimento/declínio de performance por geração de contratações */
