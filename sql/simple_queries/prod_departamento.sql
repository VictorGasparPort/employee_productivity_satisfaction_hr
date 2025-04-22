-- Query: Produtividade por Departamento (Dashboard Diário)
/* Propósito: Monitoramento operacional básico */
SELECT 
    department,
    ROUND(AVG(productivity_percent), 1) AS avg_productivity,
    ROUND(AVG(feedback_score), 2) AS avg_feedback,
    COUNT(*) FILTER (WHERE projects_completed > 5) AS high_performers
FROM main_table
GROUP BY department
ORDER BY avg_productivity DESC;
