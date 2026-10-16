from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services import thingspeak_client

router = APIRouter(prefix="/alertas", tags=["alertas"])


def _alerta(tipo: str, titulo: str, descricao: str, temperatura: float | None = None, umidade: float | None = None):
    agora = datetime.now(timezone.utc)
    return {
        "id": f"{tipo}-{int(agora.timestamp())}-{titulo[:12]}",
        "tipo": tipo,
        "titulo": titulo,
        "desc": descricao,
        "quando": agora.isoformat(),
        "temperatura": temperatura,
        "umidade": umidade,
    }


@router.get("")
def listar_alertas(
    usuario=Depends(require_role("produtor_exportador", "analista_dados", "administrador")),
):
    atual = thingspeak_client.get_ultima_leitura()
    temperatura = atual.get("temperatura")
    umidade = atual.get("umidade")
    alertas = []

    if umidade is not None and umidade > 80:
        alertas.append(_alerta("warn", "Umidade acima de 80%", "Risco aumentado de fungos. Verifique a área monitorada.", temperatura, umidade))
    elif umidade is not None and umidade < 40:
        alertas.append(_alerta("warn", "Umidade baixa", "A umidade está abaixo de 40%. Avalie a necessidade de irrigação.", temperatura, umidade))

    if temperatura is not None and temperatura > 32:
        alertas.append(_alerta("warn", "Temperatura acima de 32°C", "Calor intenso detectado na leitura mais recente.", temperatura, umidade))
    elif temperatura is not None and temperatura < 18:
        alertas.append(_alerta("info", "Temperatura baixa", "A temperatura está abaixo de 18°C.", temperatura, umidade))

    if not alertas:
        alertas.append(_alerta("ok", "Condições normais", "A última leitura está dentro dos limites monitorados.", temperatura, umidade))

    return alertas
