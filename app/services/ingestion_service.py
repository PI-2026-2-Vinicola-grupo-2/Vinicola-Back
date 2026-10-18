from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.db_models import LeituraClimatica
from app.services import thingspeak_client


def sincronizar_leituras(db: Session, resultados: int = 500) -> int:
    try:
        feeds = thingspeak_client.get_historico(resultados)
    except Exception:
        return 0

    validos = [
        f for f in feeds
        if f.get("entry_id") is not None
        and f.get("temperatura") is not None
        and f.get("umidade") is not None
        and f.get("registrado_em")
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
        reg = f["registrado_em"]
        if isinstance(reg, datetime):
            reg_dt = reg if reg.tzinfo else reg.replace(tzinfo=timezone.utc)
        elif isinstance(reg, str):
            try:
                reg_dt = datetime.fromisoformat(reg.replace("Z", "+00:00"))
            except ValueError:
                reg_dt = datetime.now(timezone.utc)
        else:
            reg_dt = datetime.now(timezone.utc)

        db.add(LeituraClimatica(
            entry_id=f["entry_id"],
            temperatura=f["temperatura"],
            umidade=f["umidade"],
            umidade_solo=f.get("umidade_solo"),
            registrado_em=reg_dt,
        ))
        novos += 1

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return 0
    except Exception:
        db.rollback()
        return 0

    return novos