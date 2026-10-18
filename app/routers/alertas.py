from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_role
from app.models.alertas import AlertaOut
from app.services import thingspeak_client

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("", response_model=list[AlertaOut])
def listar_alertas(
    usuario=Depends(require_role("produtor_exportador", "analista_dados", "administrador")),
):
    atual = thingspeak_client.get_ultima_leitura()
    entry_id = atual.get("entry_id") or 0
    temperatura = atual.get("temperatura")
    umidade = atual.get("umidade")
    umidade_solo = atual.get("umidade_solo")

    reg = atual.get("registrado_em")
    dt = None
    if isinstance(reg, datetime):
        dt = reg if reg.tzinfo else reg.replace(tzinfo=timezone.utc)
        quando = dt.isoformat()
    elif isinstance(reg, str):
        try:
            dt = datetime.fromisoformat(reg.replace("Z", "+00:00"))
        except ValueError:
            pass
        quando = reg
    else:
        quando = ""

    if dt:
        agora = datetime.now(timezone.utc)
        defasagem = int((agora - dt).total_seconds() // 60)
        if defasagem > settings.stale_minutes:
            return [{
                "id": f"sem_leituras_recentes-{entry_id}",
                "tipo": "info",
                "titulo": "Sem leituras recentes",
                "desc": f"Última leitura registrada em {quando} (há {defasagem} minutos).",
                "quando": quando,
                "temperatura": temperatura,
                "umidade": umidade,
                "umidade_solo": umidade_solo,
            }]

    alertas = []

    if umidade is not None and umidade > settings.alerta_umidade_alta:
        alertas.append({
            "id": f"umidade_alta-{entry_id}",
            "tipo": "warn",
            "titulo": f"Umidade acima de {settings.alerta_umidade_alta:.0f}%",
            "desc": "Risco aumentado de fungos. Verifique a área monitorada.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })
    elif umidade is not None and umidade < settings.alerta_umidade_baixa:
        alertas.append({
            "id": f"umidade_baixa-{entry_id}",
            "tipo": "warn",
            "titulo": "Umidade baixa",
            "desc": f"A umidade está abaixo de {settings.alerta_umidade_baixa:.0f}%. Avalie a necessidade de irrigação.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })

    if temperatura is not None and temperatura > settings.alerta_temp_alta:
        alertas.append({
            "id": f"temp_alta-{entry_id}",
            "tipo": "warn",
            "titulo": f"Temperatura acima de {settings.alerta_temp_alta:.0f}°C",
            "desc": "Calor intenso detectado na leitura mais recente.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })
    elif temperatura is not None and temperatura < settings.alerta_temp_baixa:
        alertas.append({
            "id": f"temp_baixa-{entry_id}",
            "tipo": "warn",
            "titulo": f"Temperatura abaixo de {settings.alerta_temp_baixa:.0f}°C",
            "desc": f"A temperatura está abaixo de {settings.alerta_temp_baixa:.0f}°C.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })

    if (
        settings.alerta_solo_seco is not None
        and umidade_solo is not None
        and umidade_solo < settings.alerta_solo_seco
    ):
        alertas.append({
            "id": f"solo_seco-{entry_id}",
            "tipo": "warn",
            "titulo": "Solo seco",
            "desc": f"Umidade do solo de {umidade_solo:.1f}% está abaixo do limite de {settings.alerta_solo_seco:.1f}%.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })

    if not alertas:
        alertas.append({
            "id": f"estavel-{entry_id}",
            "tipo": "ok",
            "titulo": "Condições estáveis",
            "desc": "A última leitura está dentro dos limites monitorados.",
            "quando": quando,
            "temperatura": temperatura,
            "umidade": umidade,
            "umidade_solo": umidade_solo,
        })

    return alertas
