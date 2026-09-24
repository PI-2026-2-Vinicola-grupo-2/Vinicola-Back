from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services import thingspeak_client

router = APIRouter(prefix="/clima", tags=["clima"])


@router.get("/atual")
def clima_atual():
    return thingspeak_client.get_ultima_leitura()


@router.get("/historico")
def clima_historico(resultados: int = 100, usuario=Depends(require_role("analista_dados", "administrador"))):
    return thingspeak_client.get_historico(resultados)