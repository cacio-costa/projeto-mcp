from typing import Any

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(f'{BASE_DIR}/clinica.db')


def log_query(sql):
    print(f"SQL: {sql}")


def cria_conexao() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.set_trace_callback(log_query)

    return conn


def converte_linha(linha: sqlite3.Row | None) -> dict[str, Any] | None:
    if linha is None:
        return None
    return dict(linha)


def converte_linhas(linhas: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(linha) for linha in linhas]


####
# PACIENTE
##

def busca_paciente_por_cpf(cpf: str) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            nome,
            cpf,
            telefone,
            email,
            convenio,
            criado_em
        FROM pacientes
        WHERE cpf = ?
    """

    with cria_conexao() as conn:
        linha = conn.execute(query, (cpf,)).fetchone()
        return converte_linha(linha)


def cadastra_paciente(
    nome: str,
    cpf: str,
    telefone: str,
    email: str,
    convenio: str | None = None
) -> dict[str, Any]:
    paciente_existente = busca_paciente_por_cpf(cpf)
    if paciente_existente:
        return {
            "sucesso": False,
            "mensagem": "Já existe um paciente cadastrado com esse CPF.",
            "paciente": paciente_existente,
        }

    query = """
        INSERT INTO pacientes (nome, cpf, telefone, email, convenio)
        VALUES (?, ?, ?, ?, ?)
    """

    with cria_conexao() as conn:
        cursor = conn.execute(query, (nome, cpf, telefone, email, convenio))
        conn.commit()

        paciente_id = cursor.lastrowid
        paciente = conn.execute(
            """
            SELECT id, nome, cpf, telefone, email, convenio, criado_em
            FROM pacientes
            WHERE id = ?
            """,
            (paciente_id,),
        ).fetchone()

    return {
        "sucesso": True,
        "mensagem": "Paciente cadastrado com sucesso.",
        "paciente": converte_linha(paciente),
    }


####
# MÉDICOS
##
def lista_especialidades() -> list[str]:
    query = """
        SELECT DISTINCT especialidade
        FROM medicos
        WHERE ativo = 1
        ORDER BY especialidade
    """

    with cria_conexao() as conn:
        linhas = conn.execute(query).fetchall()
        return [linha["especialidade"] for linha in linhas]


def lista_medicos_por_especialidade(especialidade: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            nome,
            especialidade,
            ativo
        FROM medicos
        WHERE LOWER(especialidade) = LOWER(?)
          AND ativo = 1
        ORDER BY nome
    """

    with cria_conexao() as conn:
        linhas = conn.execute(query, (especialidade,)).fetchall()
        return converte_linhas(linhas)


####
# HORÁRIOS
##
def lista_horarios_disponiveis(especialidade: str, data: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT
              h.id AS horario_id,
              h.data,
              h.hora,
              m.id AS medico_id,
              m.nome AS medico_nome,
              m.especialidade
         FROM horarios h
        INNER JOIN medicos m ON m.id = h.medico_id
        WHERE LOWER(m.especialidade) = LOWER(?)
          AND m.ativo = 1
          AND h.disponivel = 1
    """
    params = [especialidade]

    if data:
        query += " AND h.data = ?"
        params.append(data)

    query += """
        ORDER BY h.data, h.hora, m.nome
    """

    with cria_conexao() as conn:
        linhas = conn.execute(query, tuple(params)).fetchall()
        return converte_linhas(linhas)


def busca_horario_por_id(horario_id: int) -> dict[str, Any] | None:
    query = """
        SELECT
            h.id AS horario_id,
            h.data,
            h.hora,
            h.disponivel,
            m.id AS medico_id,
            m.nome AS medico_nome,
            m.especialidade
        FROM horarios h
        JOIN medicos m ON m.id = h.medico_id
        WHERE h.id = ?
    """

    with cria_conexao() as conn:
        linha = conn.execute(query, (horario_id,)).fetchone()
        return converte_linha(linha)


####
# CONSULTAS
##
def lista_consultas_do_paciente(cpf: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            a.id AS agendamento_id,
            a.status,
            a.observacoes,
            a.criado_em,
            p.nome AS paciente,
            p.cpf,
            m.nome AS medico,
            m.especialidade,
            h.data,
            h.hora
        FROM agendamentos a
        JOIN pacientes p ON p.id = a.paciente_id
        JOIN horarios h ON h.id = a.horario_id
        JOIN medicos m ON m.id = h.medico_id
        WHERE p.cpf = ?
        ORDER BY h.data, h.hora
    """

    with cria_conexao() as conn:
        linhas = conn.execute(query, (cpf,)).fetchall()
        return converte_linhas(linhas)


def agenda_consulta(
    cpf: str,
    horario_id: int,
    observacoes: str | None = None
) -> dict[str, Any]:
    with cria_conexao() as conn:
        paciente = busca_paciente_por_cpf(cpf)
        if not paciente:
            return {
                "sucesso": False,
                "mensagem": "Paciente não encontrado para o CPF informado.",
            }

        horario = busca_horario_por_id(horario_id)
        if not horario:
            return {
                "sucesso": False,
                "mensagem": "Horário não encontrado.",
            }

        if horario["disponivel"] == 0:
            return {
                "sucesso": False,
                "mensagem": "O horário informado não está disponível.",
            }

        cursor = conn.execute(
            """
            INSERT INTO agendamentos (paciente_id, horario_id, status, observacoes)
            VALUES (?, ?, 'agendado', ?)
            """,
            (paciente["id"], horario_id, observacoes),
        )

        conn.execute(
            """
            UPDATE horarios
            SET disponivel = 0
            WHERE id = ?
            """,
            (horario_id,),
        )

        conn.commit()

        agendamento_id = cursor.lastrowid

        agendamento = conn.execute(
            """
            SELECT
                a.id AS agendamento_id,
                a.status,
                a.observacoes,
                p.nome AS paciente_nome,
                p.cpf,
                m.nome AS medico_nome,
                m.especialidade,
                h.data,
                h.hora
            FROM agendamentos a
            JOIN pacientes p ON p.id = a.paciente_id
            JOIN horarios h ON h.id = a.horario_id
            JOIN medicos m ON m.id = h.medico_id
            WHERE a.id = ?
            """,
            (agendamento_id,),
        ).fetchone()

    return {
        "sucesso": True,
        "mensagem": "Consulta agendada com sucesso.",
        "agendamento": converte_linha(agendamento),
    }


def cancela_consulta(agendamento_id: int) -> dict[str, Any]:
    with cria_conexao() as conn:
        agendamento = conn.execute(
            """
            SELECT
                a.id,
                a.status,
                a.horario_id
            FROM agendamentos a
            WHERE a.id = ?
            """,
            (agendamento_id,),
        ).fetchone()

        if not agendamento:
            return {
                "sucesso": False,
                "mensagem": "Agendamento não encontrado.",
            }

        conn.execute(
            """
            UPDATE agendamentos
            SET status = 'cancelado'
            WHERE id = ?
            """,
            (agendamento_id,),
        )

        conn.execute(
            """
            UPDATE horarios
            SET disponivel = 1
            WHERE id = ?
            """,
            (agendamento["horario_id"],),
        )

        conn.commit()

        consulta_cancelada = conn.execute(
            """
            SELECT
                a.id AS agendamento_id,
                a.status,
                p.nome AS paciente_nome,
                p.cpf,
                m.nome AS medico_nome,
                m.especialidade,
                h.data,
                h.hora
            FROM agendamentos a
            JOIN pacientes p ON p.id = a.paciente_id
            JOIN horarios h ON h.id = a.horario_id
            JOIN medicos m ON m.id = h.medico_id
            WHERE a.id = ?
            """,
            (agendamento_id,),
        ).fetchone()

    return {
        "sucesso": True,
        "mensagem": "Consulta cancelada com sucesso.",
        "agendamento": converte_linha(consulta_cancelada),
    }

if __name__ == "__main__":
    ### TESTE RÁPIDO
    print("Especialidades:")
    print(lista_especialidades())

    print("\nPaciente por CPF:")
    print(busca_paciente_por_cpf("11111111111"))

    print("\nMédicos de Cardiologia:")
    print(lista_medicos_por_especialidade("Cardiologia"))

    print("\nHorários disponíveis em Dermatologia:")
    print(lista_horarios_disponiveis("Dermatologia"))

    print("\nConsultas do paciente 11111111111:")
    print(lista_consultas_do_paciente("11111111111"))