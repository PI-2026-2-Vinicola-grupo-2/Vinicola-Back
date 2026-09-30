"""Mede o overhead do RBAC isoladamente (RNF10). Uso: python scripts/benchmark_rbac.py"""
import statistics
import time

from app.core.security import create_access_token, get_current_user, require_role

N = 10_000
token = create_access_token(subject="bench@vinicola.com", role="administrador")
checker = require_role("administrador")


def sem_rbac():
    return {"status": "ok"}


def com_rbac():
    usuario = get_current_user(token=token)
    return checker(user=usuario)


def medir(func):
    inicio = time.perf_counter()
    for _ in range(N):
        func()
    return (time.perf_counter() - inicio) / N


tempo_sem = medir(sem_rbac)
tempo_com = medir(com_rbac)
overhead = ((tempo_com - tempo_sem) / tempo_sem) * 100

print(f"Sem RBAC: {tempo_sem * 1000:.4f} ms/chamada")
print(f"Com RBAC: {tempo_com * 1000:.4f} ms/chamada")
print(f"Overhead: {overhead:.1f}%")
print("Dentro do RNF10 (<=10%)" if overhead <= 10 else "FORA do RNF10 (>10%)")