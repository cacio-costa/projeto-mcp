PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS agendamentos;
DROP TABLE IF EXISTS horarios;
DROP TABLE IF EXISTS medicos;
DROP TABLE IF EXISTS pacientes;

CREATE TABLE pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    email TEXT NOT NULL,
    convenio TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especialidade TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medico_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    disponivel INTEGER NOT NULL DEFAULT 1 CHECK (disponivel IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medico_id) REFERENCES medicos(id)
);

CREATE TABLE agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'agendado'
        CHECK (status IN ('agendado', 'cancelado', 'realizado')),
    observacoes TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (horario_id) REFERENCES horarios(id)
);