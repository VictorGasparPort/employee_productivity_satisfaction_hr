-- Índice: Busca por Cargo e Departamento (Filtro comum em análises de RH)
CREATE INDEX idx_dept_position ON main_table (department, position)
/* Motivo: Acelera queries que combinam departamento e cargo (ex: todos gerentes de TI) 
   Considerar: Número distinto de valores e distribuição dos dados */