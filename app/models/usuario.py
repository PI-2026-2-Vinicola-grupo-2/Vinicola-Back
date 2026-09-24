from enum import Enum

from pydantic import BaseModel, EmailStr


class Perfil(str, Enum):
    produtor_exportador = "produtor_exportador"
    analista_dados = "analista_dados"
    administrador = "administrador"


class UsuarioRegistro(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Perfil


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"