import requests

from app.core.config import settings

BASE_URL = "https://api.thingspeak.com"


def _numero(valor):
    try:
        return float(valor) if valor is not None else None
    except (TypeError, ValueError):
        return None


def _formatar(f: dict) -> dict:
    return {
        "entry_id": f.get("entry_id"),
        "temperatura": _numero(f.get("field1")),
        "umidade": _numero(f.get("field2")),
        "umidade_solo": _numero(f.get("field3")),
        "registrado_em": f.get("created_at"),
    }


def get_ultima_leitura() -> dict:
    url = f"{BASE_URL}/channels/{settings.thingspeak_channel_id}/feeds/last.json"
    params = {"api_key": settings.thingspeak_read_api_key} if settings.thingspeak_read_api_key else {}
    resposta = requests.get(url, params=params, timeout=10)
    resposta.raise_for_status()
    return _formatar(resposta.json())


def get_historico(resultados: int = 100) -> list[dict]:
    url = f"{BASE_URL}/channels/{settings.thingspeak_channel_id}/feeds.json"
    params = {"results": resultados}
    if settings.thingspeak_read_api_key:
        params["api_key"] = settings.thingspeak_read_api_key
    resposta = requests.get(url, params=params, timeout=10)
    resposta.raise_for_status()
    return [_formatar(f) for f in resposta.json().get("feeds", [])]