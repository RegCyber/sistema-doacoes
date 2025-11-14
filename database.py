import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, LargeBinary, Date, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import hashlib
import secrets

# SEMPRE usa SQLite - muito mais confiável no Streamlit Cloud
DATABASE_URL = "sqlite:///doacoes.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MODELOS (exatamente iguais)
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, index=True)
    email = Column(String(200))
    whatsapp = Column(String(20))
    senha_hash = Column(String(128))
    salt = Column(String(32))
    cpf = Column(String(14), unique=True)
    is_admin = Column(Boolean, default=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    doadores = relationship("Doador", back_populates="usuario", cascade="all, delete-orphan")
    receptores = relationship("Receptor", back_populates="usuario", cascade="all, delete-orphan")
    pets = relationship("Pet", back_populates="usuario", cascade="all, delete-orphan")

class Doador(Base):
    __tablename__ = "doadores"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    cpf = Column(String(14), unique=True, index=True)
    nome = Column(String(200))
    endereco = Column(String(300))
    numero = Column(String(20))
    cep = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    telefone = Column(String(20))
    whatsapp = Column(String(20))
    pode_entregar = Column(Boolean)
    prazo_disponibilidade = Column(Date)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="doadores")
    itens = relationship("ItemDoacao", back_populates="doador", cascade="all, delete-orphan")

class ItemDoacao(Base):
    __tablename__ = "itens_doacao"
    id = Column(Integer, primary_key=True, index=True)
    doador_id = Column(Integer, ForeignKey("doadores.id"))
    item = Column(String(200))
    quantidade = Column(Integer)
    descricao = Column(Text)
    foto = Column(LargeBinary)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    doador = relationship("Doador", back_populates="itens")

class Receptor(Base):
    __tablename__ = "receptores"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    cpf = Column(String(14), unique=True, index=True)
    nome = Column(String(200))
    endereco = Column(String(300))
    numero = Column(String(20))
    cep = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    telefone = Column(String(20))
    whatsapp = Column(String(20))
    qtde_pessoas = Column(Integer)
    pode_retirar = Column(Boolean)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="receptores")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome = Column(String(100), nullable=True)
    especie = Column(String(50))
    raca = Column(String(100), nullable=True)
    descricao = Column(Text)
    situacao = Column(String(50))
    local_encontro = Column(String(200))
    contato = Column(String(20))
    foto = Column(LargeBinary, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    usuario = relationship("Usuario", back_populates="pets")

# Funções de autenticação
def gerar_salt():
    return secrets.token_hex(16)

def hash_senha(senha, salt):
    return hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def verificar_senha(senha, salt, senha_hash):
    return hash_senha(senha, salt) == senha_hash

def get_session():
    return SessionLocal()

# Cria tabelas se não existirem
def criar_tabelas():
    Base.metadata.create_all(bind=engine)

# Cria admin se não existir
def criar_admin():
    session = get_session()
    try:
        admin = session.query(Usuario).filter(Usuario.login == 'admin').first()
        if not admin:
            salt = gerar_salt()
            senha_hash = hash_senha("012admin123", salt)
            
            admin = Usuario(
                login="admin",
                email="admin@sistema.com",
                whatsapp="00000000000",
                senha_hash=senha_hash,
                salt=salt,
                cpf="00000000001",
                is_admin=True
            )
            session.add(admin)
            session.commit()
            print("✅ Admin criado!")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
    finally:
        session.close()

# Inicialização
criar_tabelas()
criar_admin()
print("🚀 Sistema pronto - usando SQLite local")
