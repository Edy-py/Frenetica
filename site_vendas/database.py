# -*- coding: utf-8 -*-
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

# --- MODELOS DAS TABELAS ---

class Estoque(Base):
    __tablename__ = 'estoque'
    id = Column(Integer, primary_key=True)
    nome_produto = Column(String, unique=True)
    quantidade = Column(Integer)
    preco_custo = Column(Float)
    preco_venda_un = Column(Float)
    preco_kit = Column(Float, nullable=True)
    personalizavel = Column(Boolean, default=False)
    foto_url = Column(String, nullable=True) # Nome do arquivo na pasta imagens/produtos

class Vendas(Base):
    __tablename__ = 'vendas'
    id = Column(Integer, primary_key=True)
    nome_prod = Column(String)
    qtd_vendida = Column(Integer)
    preco_venda_total = Column(Float)
    lucro = Column(Float)
    data = Column(DateTime, default=datetime.now)
    nome_cliente = Column(String)
    telefone = Column(String)
    tamanho = Column(String, nullable=True)
    personalizacao = Column(String, nullable=True)
    status_pagamento = Column(String, default="Pagamento Pendente")
    metodo_pagamento = Column(String)
    is_associado = Column(Boolean, default=False)

class Associados(Base):
    __tablename__ = 'associados'
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    codigo_unico = Column(String, unique=True)
    status = Column(String, default="Ativo")
    telefone = Column(String)

class Parceiros(Base):
    __tablename__ = 'parceiros'
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True)
    vantagem = Column(String)
    logo_url = Column(String, nullable=True) # Nome do arquivo na pasta imagens/parceiros

# --- CONFIGURAÇÃO DA CONEXÃO VIA SECRETS ---

@st.cache_resource
def get_engine():
    try:
        # Busca a URL configurada no arquivo secrets.toml ou no painel do Streamlit Cloud
        if "database" in st.secrets:
            db_url = st.secrets["database"]["url"]
        else:
            # Fallback local caso o segredo não seja encontrado
            return create_engine('sqlite:///frenetica_local.db')

        # Ajuste para garantir compatibilidade com o dialeto do SQLAlchemy
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        # Configurações de Pool (Crucial para o Supabase e Streamlit Cloud)
        return create_engine(
            db_url, 
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10, 
            pool_recycle=1800
        )
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return create_engine('sqlite:///frenetica_local.db')

engine = get_engine()

# --- AJUSTE AQUI: Envelopando a criação das tabelas na função que o main.py pede ---
def init_db():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        st.error(f"Erro na sincronização das tabelas: {e}")

Session = sessionmaker(bind=engine)

def get_session():
    return Session()