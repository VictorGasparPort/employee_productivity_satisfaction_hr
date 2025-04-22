-- Índice: Filtro de Alta Performance (Acelera identificação de top performers)
CREATE INDEX idx_high_performers ON main_table (name)
WHERE productivity_percent > 85 AND feedback_score >= 4.5
/* Motivo: Consultas frequentes para reconhecimento/promoções focam nesse grupo */
