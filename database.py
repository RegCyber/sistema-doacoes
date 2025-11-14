from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///doacoes.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    whatsapp = Column(String(20), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    cpf = Column(String(11), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    doadores = relationship("Doador", back_populates="usuario")
    receptores = relationship("Receptor", back_populates="usuario")
    pets = relationship("Pet", back_populates="usuario")

class Doador(Base):
    __tablename__ = 'doadores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    cep = Column(String(8), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    telefone = Column(String(20), nullable=False)
    whatsapp = Column(String(20), nullable=False)
    pode_entregar = Column(Boolean, default=False)
    prazo_disponibilidade = Column(Date, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="doadores")
    itens = relationship("ItemDoacao", back_populates="doador")

class Receptor(Base):
    __tablename__ = 'receptores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cpf = Column(String(11), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    endereco = Column(String(200), nullable=False)
    numero = Column(String(10), nullable=False)
    cep = Column(String(8), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    estado = Column(String(2), nullable=False)
    telefone = Column(String(20), nullable=False)
    whatsapp = Column(String(20), nullable=False)
    qtde_pessoas = Column(Integer, nullable=False)
    pode_retirar = Column(Boolean, default=False)
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="receptores")

class Pet(Base):
    __tablename__ = 'pets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nome = Column(String(100), nullable=True)
    especie = Column(String(50), nullable=False)
    raca = Column(String(50), nullable=True)
    descricao = Column(Text, nullable=False)
    situacao = Column(String(50), nullable=False)
    local_encontro = Column(String(200), nullable=False)
    contato = Column(String(20), nullable=False)
    foto = Column(LargeBinary, nullable=True)  # NOVO: campo para foto do pet
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="pets")

class ItemDoacao(Base):
    __tablename__ = 'itens_doacao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doador_id = Column(Integer, ForeignKey('doadores.id'))
    item = Column(String(100), nullable=False)
    quantidade = Column(Integer, nullable=False)
    descricao = Column(Text, nullable=True)
    foto = Column(LargeBinary, nullable=True)  # NOVO: campo para foto do item
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    doador = relationship("Doador", back_populates="itens")

# Funções de utilidade para senha
def gerar_salt():
    return os.urandom(16).hex()

def hash_senha(senha, salt):
    import hashlib
    return hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100000).hex()

def verificar_senha(senha, salt, senha_hash):
    return hash_senha(senha, salt) == senha_hash

# Função para obter sessão do banco
def get_session():
    return SessionLocal()

# Criar as tabelas
Base.metadata.create_all(bind=engine)

# Função para criar usuário administrador padrão
def criar_admin_padrao():
    session = get_session()
    try:
        # Verificar se já existe um admin
        admin_existente = session.query(Usuario).filter(Usuario.cpf == "00000000001").first()
        if not admin_existente:
            salt = gerar_salt()
            senha_hash = hash_senha("admin123", salt)
            
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
            print("Usuário administrador padrão criado com sucesso!")
        else:
            print("Usuário administrador já existe.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao criar admin padrão: {e}")
    finally:
        session.close()

# Criar admin padrão ao importar o módulo
criar_admin_padrao()