import requests

from app.core.config import settings

BASE_URL = "https://api.thingspeak.com"


def get_ultima_leitura() -> dict:
    url = f"{BASE_URL}/channels/{settings.thingspeak_channel_id}/feeds/last.json"
    params = {"api_key": settings.thingspeak_read_api_key} if settings.thingspeak_read_api_key else {}
    resposta = requests.get(url, params=params, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()
    return {
        "temperatura": dados.get("field1"),
        "umidade": dados.get("field2"),
        "umidade_solo": dados.get("field3"),
        "registrado_em": dados.get("created_at"),
    }


def get_historico(resultados: int = 100) -> list[dict]:
    url = f"{BASE_URL}/channels/{settings.thingspeak_channel_id}/feeds.json"
    params = {"results": resultados}
    if settings.thingspeak_read_api_key:
        params["api_key"] = settings.thingspeak_read_api_key
    resposta = requests.get(url, params=params, timeout=10)
    resposta.raise_for_status()
    feeds = resposta.json().get("feeds", [])
    return [
        {
            "temperatura": f.get("field1"),
            "umidade": f.get("field2"),
            "umidade_solo": f.get("field3"),
            "registrado_em": f.get("created_at"),
        }
        for f in feeds
    ]