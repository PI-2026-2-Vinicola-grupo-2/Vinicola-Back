from datetime import datetime

from pydantic import BaseModel


class LeituraOut(BaseModel):
    entry_id: int | None = None
    temperatura: float | None = None
    umidade: float | None = None
    umidade_solo: float | None = None
    registrado_em: datetime | None = None
    defasagem_minutos: int | None = None
    desatualizado: bool = False


class SincronizacaoOut(BaseModel):
    novas_leituras: int