import dotenv
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from api.banco import bd
dotenv.load_dotenv()

app = FastAPI(
    title="CliniFlow API",
    description="API da clínica para uso com MCP e agentes LangChain.",
    version="1.0.0",
)


# =========================
# Models
# =========================

class PacienteCreate(BaseModel):
    nome: str = Field(..., min_length=3, description="Nome completo do paciente")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF com 11 dígitos")
    telefone: str = Field(..., min_length=8, description="Telefone do paciente")
    email: str = Field(..., description="Email do paciente")
    convenio: str | None = Field(default=None, description="Convênio do paciente")


class AgendamentoCreate(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF do paciente")
    horario_id: int = Field(..., gt=0, description="ID do horário a ser agendado")
    observacoes: str | None = Field(default=None, description="Observações opcionais")


class CancelamentoCreate(BaseModel):
    agendamento_id: int = Field(..., gt=0, description="ID do agendamento a cancelar")


# =========================
# Healthcheck
# =========================

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# =========================
# Pacientes
# =========================

@app.get("/pacientes/{cpf}")
def buscar_paciente(cpf: str) -> dict[str, Any]:
    paciente = bd.busca_paciente_por_cpf(cpf)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente


@app.post("/pacientes")
def cadastrar_paciente(payload: PacienteCreate) -> dict[str, Any]:
    resultado = bd.cadastra_paciente(
        nome=payload.nome,
        cpf=payload.cpf,
        telefone=payload.telefone,
        email=payload.email,
        convenio=payload.convenio,
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=409, detail=resultado["mensagem"])

    return resultado


# =========================
# Especialidades e médicos
# =========================

@app.get("/especialidades")
def listar_especialidades() -> list[str]:
    return bd.lista_especialidades()
    # return {"especialidades": especialidades}


@app.get("/medicos")
def listar_medicos_por_especialidade(
    especialidade: str = Query(..., description="Especialidade a consultar")
) -> dict[str, Any]:
    medicos = bd.lista_medicos_por_especialidade(especialidade)
    return {
        "especialidade": especialidade,
        "quantidade": len(medicos),
        "medicos": medicos,
    }


# =========================
# Horários
# =========================

@app.get("/horarios")
def listar_horarios_disponiveis(
    especialidade: str = Query(..., description="Especialidade médica"),
    data: str | None = Query(default=None, description="Data no formato YYYY-MM-DD"),
) -> dict[str, Any]:
    horarios = bd.lista_horarios_disponiveis(especialidade=especialidade, data=data)
    return {
        "especialidade": especialidade,
        "data": data,
        "quantidade": len(horarios),
        "horarios": horarios,
    }


@app.get("/horarios/{horario_id}")
def buscar_horario(horario_id: int) -> dict[str, Any]:
    horario = bd.busca_horario_por_id(horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horário não encontrado.")
    return horario


# =========================
# Consultas
# =========================

@app.get("/consultas")
def listar_consultas_do_paciente(
    cpf: str = Query(..., description="CPF do paciente")
) -> dict[str, Any]:
    consultas = bd.lista_consultas_do_paciente(cpf)
    
    return {
        "cpf": cpf,
        "quantidade": len(consultas),
        "consultas": consultas,
    }


@app.post("/consultas")
def agendar_consulta(payload: AgendamentoCreate) -> dict[str, Any]:
    resultado = bd.agenda_consulta(
        cpf=payload.cpf,
        horario_id=payload.horario_id,
        observacoes=payload.observacoes,
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])

    return resultado


@app.put("/consultas/status/cancelada")
def cancelar_consulta(payload: CancelamentoCreate) -> dict[str, Any]:
    resultado = bd.cancela_consulta(payload.agendamento_id)

    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["mensagem"])

    return resultado