-- Tabela: Tenure Employee (Calcula tempo de casa e estágio profissional)
CREATE TABLE employee_tenure AS
/* Propósito: Analisar relação entre tempo na empresa e performance/satisfação */
SELECT 
    name,
    department,
    CURRENT_DATE - joining_date AS days_in_company,
    (projects_completed / DATE_PART('year', CURRENT_DATE - joining_date)) AS projects_per_year,
    NTILE(4) OVER (ORDER BY joining_date) AS tenure_quartile
FROM main_table
WHERE joining_date <= CURRENT_DATE;