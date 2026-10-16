from datetime import datetime

from sqlalchemy.orm import Session

from app.models.db_models import LeituraClimatica
from app.services import thingspeak_client


def sincronizar_leituras(db: Session, resultados: int = 500) -> int:
    feeds = thingspeak_client.get_historico(resultados)
    validos = [
        f for f in feeds
        if f["entry_id"] is not None
        and f["temperatura"] is not None
        and f["umidade"] is not None
        and f["registrado_em"]
    ]
    if not validos:
        return 0

    ids = [f["entry_id"] for f in validos]
    existentes = {
        e for (e,) in db.query(LeituraClimatica.entry_id).filter(LeituraClimatica.entry_id.in_(ids))
    }

    novos = 0
    for f in validos:
        if f["entry_id"] in existentes:
            continue
        db.add(LeituraClimatica(
            entry_id=f["entry_id"],
            temperatura=f["temperatura"],
            umidade=f["umidade"],
            umidade_solo=f["umidade_solo"],
            registrado_em=datetime.fromisoformat(f["registrado_em"].replace("Z", "+00:00")),
        ))
        novos += 1
    db.commit()
    return novos