BEGIN TRANSACTION;

-- Pacientes
INSERT INTO pacientes (nome, cpf, telefone, email, convenio) VALUES
('Ana Beatriz Souza', '11111111111', '11987654321', 'ana.beatriz@email.com', 'Unimed'),
('Carlos Eduardo Lima', '22222222222', '11999887766', 'carlos.lima@email.com', 'Bradesco Saúde'),
('Fernanda Alves Rocha', '33333333333', '21991234567', 'fernanda.rocha@email.com', 'SulAmérica'),
('Gustavo Henrique Martins', '44444444444', '31993456789', 'gustavo.martins@email.com', 'Amil'),
('Juliana Pereira Costa', '55555555555', '11995554433', 'juliana.costa@email.com', 'Particular'),
('Marcos Vinícius Oliveira', '66666666666', '21997778899', 'marcos.oliveira@email.com', 'NotreDame Intermédica');

-- Médicos
INSERT INTO medicos (nome, especialidade, ativo) VALUES
('Dra. Camila Torres', 'Cardiologia', 1),
('Dr. Rafael Menezes', 'Cardiologia', 1),
('Dra. Helena Duarte', 'Dermatologia', 1),
('Dr. Bruno Azevedo', 'Dermatologia', 1),
('Dr. Felipe Nogueira', 'Ortopedia', 1),
('Dra. Patrícia Barros', 'Ortopedia', 1),
('Dra. Renata Moura', 'Clínica Geral', 1),
('Dr. Diego Farias', 'Clínica Geral', 1);

-- Horários disponíveis e ocupados
-- Formato de datas: YYYY-MM-DD | horas: HH:MM
INSERT INTO horarios (medico_id, data, hora, disponivel) VALUES
-- Cardiologia - Dra. Camila Torres (id = 1)
(1, '2026-03-10', '08:00', 1),
(1, '2026-03-10', '09:00', 0),
(1, '2026-03-10', '10:00', 1),
(1, '2026-03-11', '14:00', 1),
(1, '2026-03-11', '15:00', 1),

-- Cardiologia - Dr. Rafael Menezes (id = 2)
(2, '2026-03-10', '08:30', 1),
(2, '2026-03-10', '09:30', 1),
(2, '2026-03-12', '13:00', 1),
(2, '2026-03-12', '14:00', 0),
(2, '2026-03-12', '15:00', 1),

-- Dermatologia - Dra. Helena Duarte (id = 3)
(3, '2026-03-10', '11:00', 1),
(3, '2026-03-10', '12:00', 1),
(3, '2026-03-11', '09:00', 0),
(3, '2026-03-11', '10:00', 1),
(3, '2026-03-13', '16:00', 1),

-- Dermatologia - Dr. Bruno Azevedo (id = 4)
(4, '2026-03-10', '14:00', 1),
(4, '2026-03-10', '15:00', 1),
(4, '2026-03-12', '08:00', 1),
(4, '2026-03-12', '09:00', 1),
(4, '2026-03-12', '10:00', 1),

-- Ortopedia - Dr. Felipe Nogueira (id = 5)
(5, '2026-03-11', '08:00', 1),
(5, '2026-03-11', '09:00', 1),
(5, '2026-03-11', '10:00', 0),
(5, '2026-03-13', '13:00', 1),
(5, '2026-03-13', '14:00', 1),

-- Ortopedia - Dra. Patrícia Barros (id = 6)
(6, '2026-03-10', '16:00', 1),
(6, '2026-03-10', '17:00', 1),
(6, '2026-03-12', '11:00', 1),
(6, '2026-03-12', '12:00', 1),
(6, '2026-03-12', '13:00', 1),

-- Clínica Geral - Dra. Renata Moura (id = 7)
(7, '2026-03-10', '08:00', 1),
(7, '2026-03-10', '09:00', 1),
(7, '2026-03-10', '10:00', 1),
(7, '2026-03-11', '11:00', 1),
(7, '2026-03-11', '12:00', 1),

-- Clínica Geral - Dr. Diego Farias (id = 8)
(8, '2026-03-10', '13:00', 1),
(8, '2026-03-10', '14:00', 1),
(8, '2026-03-12', '15:00', 1),
(8, '2026-03-12', '16:00', 1),
(8, '2026-03-12', '17:00', 1);

-- Agendamentos existentes
-- Estes registros correspondem a horários marcados como indisponíveis no INSERT acima
INSERT INTO agendamentos (paciente_id, horario_id, status, observacoes) VALUES
(1, 2, 'agendado', 'Retorno cardiológico'),
(3, 9, 'agendado', 'Avaliação de exames'),
(5, 13, 'agendado', 'Consulta dermatológica inicial'),
(2, 23, 'agendado', 'Dor no joelho há 2 semanas');

COMMIT;