from pydantic import BaseModel


class DiaPrevisao(BaseModel):
    data: str
    temperatura: float
    umidade: float
    pontuacao: int
    icone: str


class PrevisaoOut(BaseModel):
    melhor_dia: str
    confianca: int | None = None
    metodo: str
    dias: list[DiaPrevisao]
    simulado: bool = True
    dias_de_historico: int
    aviso: str
