-- Tabela: Faixas Salariais Estratégicas (Categoriza salários para políticas de RH)
CREATE TABLE salary_bands (
    band VARCHAR(10) PRIMARY KEY,
    min_salary NUMERIC,
    max_sERIC NUMERIC,
    benchmark_ratio NUMERIC
);
/* Propósito: Facilitar comparações de equidade salarial e planejamento orçamentário */
INSERT INTO salary_bands VALUES
('Junior', 0, 5000, 1.0),
('Mid', 5001, 10000, 1.2),
('Senior', 10001, 20000, 1.5),
('Executive', 20001, 999999, 2.0);