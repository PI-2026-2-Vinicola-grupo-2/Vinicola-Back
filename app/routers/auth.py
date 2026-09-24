from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Token, UsuarioLogin, UsuarioRegistro

router = APIRouter(prefix="/auth", tags=["auth"])

# Armazenamento temporário em memória — troca pelo banco de verdade no passo 6 (Vinicola-BD)
_usuarios: dict[str, dict] = {}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(dados: UsuarioRegistro):
    if dados.email in _usuarios:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
    _usuarios[dados.email] = {
        "nome": dados.nome,
        "senha_hash": hash_password(dados.senha),
        "perfil": dados.perfil.value,
    }
    return {"mensagem": "Usuário criado com sucesso"}


@router.post("/login", response_model=Token)
def login(dados: UsuarioLogin):
    usuario = _usuarios.get(dados.email)
    if not usuario or not verify_password(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    token = create_access_token(subject=dados.email, role=usuario["perfil"])
    return Token(access_token=token)