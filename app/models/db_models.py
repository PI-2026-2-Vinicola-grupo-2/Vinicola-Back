from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.core.database import Base


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class LeituraClimatica(Base):
    __tablename__ = "leituras_climaticas"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, unique=True, index=True, nullable=True)
    temperatura = Column(Float, nullable=False)
    umidade = Column(Float, nullable=False)
    umidade_solo = Column(Float, nullable=True)
    registrado_em = Column(DateTime(timezone=True), nullable=False, index=True)
    inserido_em = Column(DateTime(timezone=True), server_default=func.now())


class DadoMercado(Base):
    __tablename__ = "dados_mercado"

    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    demanda = Column(String, nullable=True)
    registrado_em = Column(DateTime(timezone=True), nullable=False)


class Previsao(Base):
    __tablename__ = "previsoes"

    id = Column(Integer, primary_key=True, index=True)
    janela_inicio = Column(Date, nullable=False)
    janela_fim = Column(Date, nullable=False)
    confianca = Column(Float, nullable=True)
    gerado_em = Column(DateTime(timezone=True), server_default=func.now())


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    previsao_id = Column(Integer, ForeignKey("previsoes.id"), nullable=False)
    mensagem = Column(Text, nullable=False)
    nivel = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    visualizado = Column(Boolean, default=False)