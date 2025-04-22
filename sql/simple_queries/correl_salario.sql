-- Query: Correlação Salário-Satisfação (Relatório de Equidade)
/* Propósito: Verificar se salários mais altos correlacionam com maior satisfação */
SELECT 
    CORR(salary, satisfaction_rate_percent) AS salary_satisfaction_corr,
    CORR(salary, productivity_percent) AS salary_productivity_corr
FROM main_table
WHERE department != 'Executivo';  -- Exclui outliers