-- Particionamento: Segmentação por Faixa Salarial
CREATE TABLE main_table_partitioned PARTITION BY RANGE (salary) (
    PARTITION low_income VALUES LESS THAN (5000),
    PARTITION mid_income VALUES LESS THAN (10000),
    PARTITION high_income VALUES LESS THAN (MAXVALUE)
);
/* Motivo: Acelera relatórios de equidade salarial e auditorias por faixa de renda */