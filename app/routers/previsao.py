from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services import thingspeak_client

router = APIRouter(prefix="/previsao", tags=["previsao"])


def _media(valores):
    valores = [v for v in valores if v is not None]
    return sum(valores) / len(valores) if valores else None


def _pontuacao(temperatura, umidade):
    if temperatura is None or umidade is None:
        return 0
    score = 100
    if temperatura < 22:
        score -= (22 - temperatura) * 3
    elif temperatura > 30:
        score -= (temperatura - 30) * 4
    if umidade < 50:
        score -= (50 - umidade) * 0.7
    elif umidade > 75:
        score -= (umidade - 75) * 1.2
    return max(0, min(100, round(score)))


@router.get("/janela-colheita")
def janela_colheita(
    usuario=Depends(require_role("produtor_exportador", "analista_dados", "administrador")),
):
    historico = thingspeak_client.get_historico(200)
    temperaturas = [x.get("temperatura") for x in historico]
    umidades = [x.get("umidade") for x in historico]
    temp_media = _media(temperaturas)
    umi_media = _media(umidades)

    agora = datetime.now(timezone.utc)
    dias = []
    for i in range(7):
        data = agora + timedelta(days=i)
        variacao_t = ((i % 3) - 1) * 0.7
        variacao_u = ((i % 2) * 2) - 1
        temperatura = round((temp_media if temp_media is not None else 26) + variacao_t, 1)
        umidade = round((umi_media if umi_media is not None else 60) + variacao_u, 1)
        pontuacao = _pontuacao(temperatura, umidade)
        dias.append({
            "data": data.date().isoformat(),
            "temperatura": temperatura,
            "umidade": umidade,
            "pontuacao": pontuacao,
            "icone": "☀️" if umidade < 65 else "⛅",
        })

    melhor = max(dias, key=lambda x: x["pontuacao"])
    return {
        "melhor_dia": melhor["data"],
        "confianca": 60 if historico else 20,
        "metodo": "estimativa baseada no histórico do ThingSpeak",
        "dias": dias,
    }
