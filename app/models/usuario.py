from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class Perfil(str, Enum):
    produtor_exportador = "produtor_exportador"
    analista_dados = "analista_dados"
    administrador = "administrador"


class UsuarioRegistro(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    perfil: Perfil


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nome: str
    perfil: Perfil