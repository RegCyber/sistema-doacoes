import os
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pandas as pd
import hashlib
import secrets

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    whatsapp = Column(String(15))
    senha_hash = Column(String(128), nullable=False)  # SHA512
    salt = Column(String(32), nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)

class Doador(Base):
    __tablename__ = 'doadores'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)  # Pode ser anônimo
    cpf = Column(String(14), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    cep = Column(String(9), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    telefone = Column(String(15), nullable=False)
    whatsapp = Column(String(15), nullable=False)
    pode_entregar = Column(Boolean, default=False)
    prazo_disponibilidade = Column(Date, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    usuario = relationship("Usuario", backref="doacoes")
    itens = relationship("ItemDoacao", backref="doador", cascade="all, delete-orphan")

class ItemDoacao(Base):
    __tablename__ = 'itens_doacao'
    
    id = Column(Integer, primary_key=True)
    doador_id = Column(Integer, ForeignKey('doadores.id'), nullable=False)
    item = Column(String(200), nullable=False)
    quantidade = Column(Integer, nullable=False)
    descricao = Column(Text)
    foto_url = Column(String(500))
    data_cadastro = Column(DateTime, default=datetime.utcnow)

class Receptor(Base):
    __tablename__ = 'receptores'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    cpf = Column(String(14), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    cep = Column(String(9), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    telefone = Column(String(15), nullable=False)
    whatsapp = Column(String(15), nullable=False)
    qtde_pessoas = Column(Integer, nullable=False)
    pode_retirar = Column(Boolean, default=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", backref="solicitacoes")

class Pet(Base):
    __tablename__ = 'pets'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    nome = Column(String(100))
    especie = Column(String(50), nullable=False)
    raca = Column(String(50))
    descricao = Column(Text, nullable=False)
    foto = Column(String(500))
    situacao = Column(String(20), nullable=False)
    local_encontro = Column(String(200))
    contato = Column(String(100), nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", backref="pets")

# Funções de segurança
def gerar_salt():
    return secrets.token_hex(16)

def hash_senha(senha, salt):
    return hashlib.sha512((senha + salt).encode()).hexdigest()

def verificar_senha(senha, salt, senha_hash):
    return hash_senha(senha, salt) == senha_hash

def get_database_url():
    # Para produção (Streamlit Cloud)
    if 'DATABASE_URL' in os.environ:
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Para desenvolvimento
    return 'sqlite:///doacoes.db'

def init_db():
    engine = create_engine(get_database_url())
    
    # Criar todas as tabelas
    Base.metadata.create_all(engine)
    
    # Criar usuário admin padrão se não existir
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        admin_existe = session.query(Usuario).filter(Usuario.login == 'PIUNIVESP').first()
        if not admin_existe:
            salt = gerar_salt()
            senha_hash = hash_senha('2025Univesp', salt)
            admin = Usuario(
                login='PIUNIVESP',
                email='admin@sistema-doacoes.com',
                senha_hash=senha_hash,
                salt=salt,
                is_admin=True
            )
            session.add(admin)
            session.commit()
            print("✅ Usuário administrador criado: PIUNIVESP / 2025Univesp")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        session.rollback()
    finally:
        session.close()
    
    return engine

def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()