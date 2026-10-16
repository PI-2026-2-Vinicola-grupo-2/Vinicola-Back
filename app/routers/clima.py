from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.services import thingspeak_client
from app.services.ingestion_service import sincronizar_leituras

router = APIRouter(prefix="/clima", tags=["clima"])


@router.get("/atual")
def clima_atual():
    return thingspeak_client.get_ultima_leitura()


@router.get("/historico")
def clima_historico(
    resultados: int = 100,
    usuario=Depends(require_role("produtor_exportador", "analista_dados", "administrador")),
):
    return thingspeak_client.get_historico(resultados)


@router.post("/sincronizar")
def sincronizar(
    resultados: int = 500,
    db: Session = Depends(get_db),
    usuario=Depends(require_role("administrador")),
):
    return {"novas_leituras": sincronizar_leituras(db, min(resultados, 8000))}