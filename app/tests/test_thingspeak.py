from app.services.thingspeak_client import _formatar, _numero


def test_numero_e_formatar_convertem_strings():
    assert _numero("25.80") == 25.8
    assert _numero("não-numérico") is None
    assert _formatar(
        {
            "entry_id": 7,
            "field1": "25.80",
            "field2": "61.20",
            "field3": "40",
            "created_at": "2026-10-18T12:00:00Z",
        }
    ) == {
        "entry_id": 7,
        "temperatura": 25.8,
        "umidade": 61.2,
        "umidade_solo": 40.0,
        "registrado_em": "2026-10-18T12:00:00Z",
    }
