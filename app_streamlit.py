import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_session, Doador, Receptor, Pet, ItemDoacao, Usuario
from database import hash_senha, gerar_salt, verificar_senha
#from database import engine, Base
from database import Base, init_db 
import os

# try:
#     # Força a recriação do banco usando a função init_db do seu database.py
#     engine = init_db()
#     st.sidebar.success("✅ Banco inicializado com sucesso!")
    
#     # Opcional: verificar se as tabelas foram criadas
#     from sqlalchemy import inspect
#     inspector = inspect(engine)
#     tabelas = inspector.get_table_names()
#     st.sidebar.info(f"📊 Tabelas criadas: {len(tabelas)}")
    
# except Exception as e:
#     st.sidebar.error(f"❌ Erro: {e}")

# Configuração da página
st.set_page_config(
    page_title="Sistema de Doações para Enchentes",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .pet-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: white;
    }
    .item-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de autenticação
def inicializar_sessao():
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'itens' not in st.session_state:
        st.session_state.itens = [{'item': '', 'quantidade': 1, 'descricao': '', 'foto_url': ''}]

def fazer_login(login, senha):
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.login == login).first()
        if usuario and verificar_senha(senha, usuario.salt, usuario.senha_hash):
            st.session_state.usuario_logado = usuario.login
            st.session_state.is_admin = usuario.is_admin
            st.session_state.user_id = usuario.id
            return True
        return False
    finally:
        session.close()

def fazer_logout():
    st.session_state.usuario_logado = None
    st.session_state.is_admin = False
    st.session_state.user_id = None
    st.session_state.itens = [{'item': '', 'quantidade': 1, 'descricao': '', 'foto_url': ''}]

def cadastrar_usuario(login, email, whatsapp, senha):
    session = get_session()
    try:
        # Verificar se usuário já existe
        existe = session.query(Usuario).filter(Usuario.login == login).first()
        if existe:
            return False, "Usuário já existe"
        
        if len(senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        salt = gerar_salt()
        senha_hash = hash_senha(senha, salt)
        
        novo_usuario = Usuario(
            login=login,
            email=email,
            whatsapp=whatsapp,
            senha_hash=senha_hash,
            salt=salt
        )
        
        session.add(novo_usuario)
        session.commit()
        return True, "Usuário cadastrado com sucesso!"
        
    except Exception as e:
        session.rollback()
        return False, f"Erro ao cadastrar: {e}"
    finally:
        session.close()

# Inicializar sessão
inicializar_sessao()

# Sidebar com informações de login
st.sidebar.title("🎯 Navegação")

if st.session_state.usuario_logado:
    st.sidebar.success(f"👤 Logado como: {st.session_state.usuario_logado}")
    if st.session_state.is_admin:
        st.sidebar.info("⚡ Modo Administrador")
    if st.sidebar.button("🚪 Sair"):
        fazer_logout()
        st.rerun()
else:
    # Menu de login/cadastro na sidebar
    opcao_login = st.sidebar.radio("Acesso:", ["Entrar", "Cadastrar"])
    
    if opcao_login == "Entrar":
        with st.sidebar.form("login_form"):
            st.subheader("🔐 Login")
            login = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if fazer_login(login, senha):
                    st.sidebar.success("Login realizado!")
                    st.rerun()
                else:
                    st.sidebar.error("Usuário ou senha inválidos")
    
    else:  # Cadastro
        with st.sidebar.form("cadastro_form"):
            st.subheader("📝 Cadastro")
            login = st.text_input("Nome de usuário*")
            email = st.text_input("E-mail")
            whatsapp = st.text_input("WhatsApp")
            senha = st.text_input("Senha (mínimo 6 caracteres)*", type="password")
            if st.form_submit_button("Cadastrar"):
                sucesso, mensagem = cadastrar_usuario(login, email, whatsapp, senha)
                if sucesso:
                    st.sidebar.success(mensagem)
                else:
                    st.sidebar.error(mensagem)

# Páginas principais (só aparecem se não estiver na tela de login)
if not st.session_state.usuario_logado and 'opcao_login' in locals() and opcao_login == "Entrar":
    st.title("🔐 Sistema de Doações para Enchentes")
    st.info("Faça login na sidebar para acessar o sistema completo.")
    
else:
    # Menu principal (apenas para usuários logados ou acesso anônimo limitado)
    if st.session_state.usuario_logado:
        paginas = ["🏠 Início", "🎁 Cadastrar Doação", "🆘 Solicitar Ajuda", "🐾 Pets Perdidos", "📊 Visualizar Cadastros"]
        if st.session_state.is_admin:
            paginas.append("⚡ Administração")
    else:
        paginas = ["🏠 Início", "📊 Visualizar Cadastros"]
        st.sidebar.warning("⚠️ Faça login para cadastrar doações")
    
    pagina = st.sidebar.radio("Selecione a página:", paginas)

    # Sessão do banco
    session = get_session()

    # Página Inicial
    if pagina == "🏠 Início":
        st.markdown('<h1 class="main-header">🤝 Solidariedade em Tempos de Enchente</h1>', unsafe_allow_html=True)
        
        st.write("""
        ## Juntos somos mais fortes!
        
        Esta plataforma conecta pessoas que querem ajudar com quem precisa de ajuda durante enchentes. 
        Sua solidariedade pode fazer a diferença!
        """)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_doadores = session.query(Doador).count()
            st.metric("👥 Doadores", total_doadores)
        
        with col2:
            total_itens = session.query(ItemDoacao).count()
            st.metric("📦 Itens", total_itens)
        
        with col3:
            total_receptores = session.query(Receptor).count()
            st.metric("🆘 Pessoas", total_receptores)
        
        with col4:
            total_pets = session.query(Pet).count()
            st.metric("🐾 Pets", total_pets)

    # Cadastrar Doação - VERSÃO CORRIGIDA
    elif pagina == "🎁 Cadastrar Doação" and st.session_state.usuario_logado:
        st.title("🎁 Cadastrar Doação")
        
        # Controles para adicionar/remover itens (FORA do formulário)
        st.subheader("🎁 Itens para Doação")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Adicione um ou mais itens que deseja doar:")
        with col2:
            if st.button("➕ Adicionar Novo Item"):
                st.session_state.itens.append({'item': '', 'quantidade': 1, 'descricao': '', 'foto_url': ''})
                st.rerun()
        
        # Resumo dos itens antes do formulário
        if len(st.session_state.itens) > 0:
            itens_validos = [item for item in st.session_state.itens if item['item']]
            if itens_validos:
                st.subheader("📋 Resumo dos Itens")
                total_itens = sum(item['quantidade'] for item in itens_validos)
                st.write(f"**Total de itens diferentes:** {len(itens_validos)}")
                st.write(f"**Quantidade total:** {total_itens}")
                
                # Lista resumida
                for i, item_data in enumerate(itens_validos):
                    st.write(f"• {item_data['quantidade']}x {item_data['item']}")
        
        with st.form("form_doador"):
            st.subheader("📋 Dados Pessoais do Doador")
            col1, col2 = st.columns(2)
            
            with col1:
                cpf = st.text_input("CPF*", placeholder="000.000.000-00")
                nome = st.text_input("Nome Completo*")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999")
                pode_entregar = st.selectbox("Pode entregar os itens?*", ["", "Sim", "Não"])
            
            st.subheader("🏠 Endereço")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000")
                endereco = st.text_input("Endereço*")
                numero = st.text_input("Número*")
            
            with col2:
                bairro = st.text_input("Bairro*")
                cidade = st.text_input("Cidade*")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2)
            
            st.subheader("⏰ Disponibilidade")
            prazo_disponibilidade = st.date_input("Prazo de Disponibilidade*", min_value=datetime.today())
            
            # Mostrar itens atuais no formulário
            itens_para_remover = []
            
            for i, item_data in enumerate(st.session_state.itens):
                with st.expander(f"Item {i+1}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        item = st.text_input(
                            f"Item*",
                            value=item_data['item'],
                            placeholder="Ex: Arroz, Roupas, Colchão, Medicamentos...",
                            key=f"item_{i}"
                        )
                        
                        col_qtd, col_desc = st.columns(2)
                        with col_qtd:
                            quantidade = st.number_input(
                                f"Quantidade*",
                                min_value=1,
                                value=item_data['quantidade'],
                                key=f"qtd_{i}"
                            )
                        with col_desc:
                            descricao = st.text_area(
                                f"Descrição",
                                value=item_data['descricao'],
                                placeholder="Detalhes, marca, estado do item...",
                                height=80,
                                key=f"desc_{i}"
                            )
                        
                        foto_url = st.text_input(
                            f"URL da Foto (opcional)",
                            value=item_data['foto_url'],
                            placeholder="https://exemplo.com/foto-item.jpg",
                            key=f"foto_{i}"
                        )
                    
                    with col2:
                        st.write("")  # Espaçamento
                        st.write("")  # Espaçamento
                        if len(st.session_state.itens) > 1:
                            # Usar checkbox para remover (dentro do form é permitido)
                            if st.checkbox("Remover", key=f"remove_{i}"):
                                itens_para_remover.append(i)
                    
                    # Atualiza os dados do item
                    st.session_state.itens[i] = {
                        'item': item,
                        'quantidade': quantidade,
                        'descricao': descricao,
                        'foto_url': foto_url
                    }
            
            # Botão de submit do formulário
            submitted = st.form_submit_button("📝 Cadastrar Doação")
            
            if submitted:
                # Remove itens marcados para remoção (de trás para frente)
                for i in sorted(itens_para_remover, reverse=True):
                    st.session_state.itens.pop(i)
                
                # Validações
                campos_pessoais_ok = all([cpf, nome, telefone, whatsapp, pode_entregar, cep, endereco, numero, bairro, cidade, estado])
                
                # Verifica se há pelo menos 1 item preenchido
                itens_validos = [item for item in st.session_state.itens if item['item']]
                if not itens_validos:
                    st.error("⚠️ Adicione pelo menos um item para doação!")
                    campos_pessoais_ok = False
                
                if campos_pessoais_ok:
                    try:
                        # Obter usuário logado
                        usuario_id = st.session_state.user_id if st.session_state.usuario_logado else None
                        
                        # Cadastra o doador
                        novo_doador = Doador(
                            usuario_id=usuario_id,
                            cpf=cpf,
                            nome=nome,
                            endereco=endereco,
                            numero=numero,
                            cep=cep,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            telefone=telefone,
                            whatsapp=whatsapp,
                            pode_entregar=pode_entregar == "Sim",
                            prazo_disponibilidade=prazo_disponibilidade
                        )
                        session.add(novo_doador)
                        session.flush()  # Para obter o ID do doador
                        
                        # Cadastra os itens
                        for item_data in itens_validos:
                            novo_item = ItemDoacao(
                                doador_id=novo_doador.id,
                                item=item_data['item'],
                                quantidade=item_data['quantidade'],
                                descricao=item_data['descricao'] if item_data['descricao'] else None,
                                foto_url=item_data['foto_url'] if item_data['foto_url'] else None
                            )
                            session.add(novo_item)
                        
                        session.commit()
                        
                        st.success("✅ Doação cadastrada com sucesso!")
                        st.balloons()
                        
                        # Mostra resumo final
                        st.info(f"""
                        **Resumo do cadastro:**
                        - **Doador:** {nome}
                        - **Itens cadastrados:** {len(itens_validos)}
                        - **Quantidade total:** {sum(item['quantidade'] for item in itens_validos)}
                        - **Disponível até:** {prazo_disponibilidade.strftime('%d/%m/%Y')}
                        """)
                        
                        # Limpa o formulário
                        st.session_state.itens = [{'item': '', 'quantidade': 1, 'descricao': '', 'foto_url': ''}]
                        
                    except Exception as e:
                        session.rollback()
                        st.error(f"❌ Erro ao cadastrar doação: {e}")
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios!")

    # Solicitar Ajuda (Receptor)
    elif pagina == "🆘 Solicitar Ajuda" and st.session_state.usuario_logado:
        st.title("🆘 Solicitar Ajuda")
        
        with st.form("form_receptor"):
            st.subheader("📋 Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                cpf = st.text_input("CPF*", placeholder="000.000.000-00", key="rec_cpf")
                nome = st.text_input("Nome Completo*", key="rec_nome")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999", key="rec_tel")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999", key="rec_whats")
                qtde_pessoas = st.number_input("Quantidade de Pessoas*", min_value=1, value=1, key="rec_pessoas")
                pode_retirar = st.selectbox("Pode retirar os itens?*", ["", "Sim", "Não"], key="rec_retirar")
            
            st.subheader("🏠 Endereço para Entrega")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000", key="rec_cep")
                endereco = st.text_input("Endereço*", key="rec_end")
                numero = st.text_input("Número*", key="rec_num")
            
            with col2:
                bairro = st.text_input("Bairro*", key="rec_bairro")
                cidade = st.text_input("Cidade*", key="rec_cidade")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2, key="rec_estado")
            
            st.subheader("💬 Observações")
            observacoes = st.text_area("Descreva brevemente sua situação e necessidades:", 
                                     placeholder="Ex: Perdi tudo na enchente, preciso de roupas, colchões e alimentos...")
            
            submitted = st.form_submit_button("📝 Solicitar Ajuda")
            
            if submitted:
                campos_ok = all([cpf, nome, telefone, whatsapp, cep, endereco, numero, bairro, cidade, estado, pode_retirar])
                
                if campos_ok:
                    try:
                        usuario_id = st.session_state.user_id if st.session_state.usuario_logado else None
                        
                        novo_receptor = Receptor(
                            usuario_id=usuario_id,
                            cpf=cpf,
                            nome=nome,
                            endereco=endereco,
                            numero=numero,
                            cep=cep,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            telefone=telefone,
                            whatsapp=whatsapp,
                            qtde_pessoas=qtde_pessoas,
                            pode_retirar=pode_retirar == "Sim"
                        )
                        
                        session.add(novo_receptor)
                        session.commit()
                        
                        st.success("✅ Solicitação de ajuda cadastrada com sucesso!")
                        st.balloons()
                        
                        st.info(f"""
                        **Resumo do cadastro:**
                        - **Solicitante:** {nome}
                        - **Pessoas na família:** {qtde_pessoas}
                        - **Pode retirar:** {pode_retirar}
                        - **Entregar em:** {endereco}, {numero} - {bairro}, {cidade}-{estado}
                        """)
                        
                    except Exception as e:
                        session.rollback()
                        st.error(f"❌ Erro ao cadastrar solicitação: {e}")
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios!")

    # Pets Perdidos
    elif pagina == "🐾 Pets Perdidos" and st.session_state.usuario_logado:
        st.title("🐾 Pets Perdidos/Encontrados")
        
        tab1, tab2 = st.tabs(["📝 Cadastrar Pet", "👀 Ver Pets Cadastrados"])
        
        with tab1:
            with st.form("form_pet"):
                st.subheader("📋 Dados do Pet")
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome do Pet", placeholder="Opcional")
                    especie = st.selectbox("Espécie*", ["", "Cachorro", "Gato", "Ave", "Outro"])
                    raca = st.text_input("Raça", placeholder="Opcional")
                
                with col2:
                    situacao = st.selectbox("Situação*", ["", "Perdido", "Encontrado", "Para Adoção"])
                    local_encontro = st.text_input("Local onde foi encontrado/perdido*")
                    contato = st.text_input("Contato para informações*", placeholder="Telefone/WhatsApp")
                
                descricao = st.text_area("Descrição do Pet*", 
                                       placeholder="Cor, tamanho, características especiais, comportamento...")
                foto_url = st.text_input("URL da Foto (opcional)", placeholder="https://exemplo.com/foto-pet.jpg")
                
                submitted = st.form_submit_button("🐾 Cadastrar Pet")
                
                if submitted:
                    campos_ok = all([especie, descricao, local_encontro, contato, situacao])
                    
                    if campos_ok:
                        try:
                            usuario_id = st.session_state.user_id if st.session_state.usuario_logado else None
                            
                            novo_pet = Pet(
                                usuario_id=usuario_id,
                                nome=nome if nome else None,
                                especie=especie,
                                raca=raca if raca else None,
                                descricao=descricao,
                                foto=foto_url if foto_url else None,
                                situacao=situacao,
                                local_encontro=local_encontro,
                                contato=contato
                            )
                            
                            session.add(novo_pet)
                            session.commit()
                            
                            st.success("✅ Pet cadastrado com sucesso!")
                            st.balloons()
                            
                        except Exception as e:
                            session.rollback()
                            st.error(f"❌ Erro ao cadastrar pet: {e}")
                    else:
                        st.error("⚠️ Preencha todos os campos obrigatórios!")
        
        with tab2:
            st.subheader("📋 Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("🐾 Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            if pet.foto:
                                st.image(pet.foto, width=150)
                            else:
                                st.image("https://via.placeholder.com/150x150?text=Pet", width=150)
                        
                        with col2:
                            st.write(f"**{pet.nome if pet.nome else 'Sem nome'}**")
                            st.write(f"**Espécie:** {pet.especie} | **Raça:** {pet.raca if pet.raca else 'Não informada'}")
                            st.write(f"**Situação:** {pet.situacao} | **Local:** {pet.local_encontro}")
                            st.write(f"**Descrição:** {pet.descricao}")
                            st.write(f"**Contato:** {pet.contato}")
                            st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
                        
                        st.divider()

    # Visualizar Cadastros
    elif pagina == "📊 Visualizar Cadastros":
        st.title("📊 Visualizar Cadastros")
        
        tab1, tab2, tab3 = st.tabs(["🎁 Doações", "🆘 Solicitações", "🐾 Pets"])
        
        with tab1:
            st.subheader("🎁 Doações Cadastradas")
            doadores = session.query(Doador).all()
            
            if not doadores:
                st.info("Nenhuma doação cadastrada ainda.")
            else:
                for doador in doadores:
                    with st.expander(f"🧍 {doador.nome} - {doador.cidade}/{doador.estado}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**CPF:** {doador.cpf}")
                            st.write(f"**Telefone:** {doador.telefone}")
                            st.write(f"**WhatsApp:** {doador.whatsapp}")
                            st.write(f"**Pode entregar:** {'Sim' if doador.pode_entregar else 'Não'}")
                            st.write(f"**Disponível até:** {doador.prazo_disponibilidade.strftime('%d/%m/%Y')}")
                        
                        with col2:
                            st.write(f"**Endereço:** {doador.endereco}, {doador.numero}")
                            st.write(f"**Bairro:** {doador.bairro}")
                            st.write(f"**CEP:** {doador.cep}")
                            st.write(f"**Cidade/Estado:** {doador.cidade}/{doador.estado}")
                        
                        # Itens doados
                        if doador.itens:
                            st.write("**Itens para doação:**")
                            for item in doador.itens:
                                st.write(f"• {item.quantidade}x {item.item}" + 
                                       (f" - {item.descricao}" if item.descricao else ""))
        
        with tab2:
            st.subheader("🆘 Solicitações de Ajuda")
            receptores = session.query(Receptor).all()
            
            if not receptores:
                st.info("Nenhuma solicitação de ajuda cadastrada ainda.")
            else:
                for receptor in receptores:
                    with st.expander(f"🧍 {receptor.nome} - {receptor.cidade}/{receptor.estado}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**CPF:** {receptor.cpf}")
                            st.write(f"**Telefone:** {receptor.telefone}")
                            st.write(f"**WhatsApp:** {receptor.whatsapp}")
                            st.write(f"**Pessoas na família:** {receptor.qtde_pessoas}")
                            st.write(f"**Pode retirar:** {'Sim' if receptor.pode_retirar else 'Não'}")
                        
                        with col2:
                            st.write(f"**Endereço:** {receptor.endereco}, {receptor.numero}")
                            st.write(f"**Bairro:** {receptor.bairro}")
                            st.write(f"**CEP:** {receptor.cep}")
                            st.write(f"**Cidade/Estado:** {receptor.cidade}/{receptor.estado}")
        
        with tab3:
            st.subheader("🐾 Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    with st.expander(f"{pet.nome if pet.nome else 'Sem nome'} - {pet.situacao}", expanded=False):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if pet.foto:
                                st.image(pet.foto, width=150)
                            else:
                                st.image("https://via.placeholder.com/150x150?text=Pet", width=150)
                        
                        with col2:
                            st.write(f"**Espécie:** {pet.especie}")
                            st.write(f"**Raça:** {pet.raca if pet.raca else 'Não informada'}")
                            st.write(f"**Situação:** {pet.situacao}")
                            st.write(f"**Local:** {pet.local_encontro}")
                            st.write(f"**Descrição:** {pet.descricao}")
                            st.write(f"**Contato:** {pet.contato}")
                            st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")

    # Administração (apenas para admin)
    elif pagina == "⚡ Administração" and st.session_state.is_admin:
        st.title("⚡ Área Administrativa")
        
        st.subheader("📈 Estatísticas do Sistema")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_usuarios = session.query(Usuario).count()
            st.metric("👥 Total de Usuários", total_usuarios)
        
        with col2:
            total_doadores = session.query(Doador).count()
            st.metric("🎁 Doadores", total_doadores)
        
        with col3:
            total_receptores = session.query(Receptor).count()
            st.metric("🆘 Solicitantes", total_receptores)
        
        with col4:
            total_pets = session.query(Pet).count()
            st.metric("🐾 Pets", total_pets)
        
        st.subheader("📊 Relatórios")
        
        # Exportar dados
        if st.button("📥 Exportar Dados para Excel"):
            try:
                # Doadores
                doadores_data = []
                for doador in session.query(Doador).all():
                    doadores_data.append({
                        'Nome': doador.nome,
                        'CPF': doador.cpf,
                        'Telefone': doador.telefone,
                        'Cidade': doador.cidade,
                        'Estado': doador.estado,
                        'Data Cadastro': doador.data_cadastro
                    })
                
                # Receptores
                receptores_data = []
                for receptor in session.query(Receptor).all():
                    receptores_data.append({
                        'Nome': receptor.nome,
                        'CPF': receptor.cpf,
                        'Telefone': receptor.telefone,
                        'Cidade': receptor.cidade,
                        'Pessoas': receptor.qtde_pessoas,
                        'Data Cadastro': receptor.data_cadastro
                    })
                
                # Criar Excel com múltiplas abas
                with pd.ExcelWriter('relatorio_doacoes.xlsx') as writer:
                    pd.DataFrame(doadores_data).to_excel(writer, sheet_name='Doadores', index=False)
                    pd.DataFrame(receptores_data).to_excel(writer, sheet_name='Solicitantes', index=False)
                
                st.success("✅ Relatório exportado com sucesso!")
                st.download_button(
                    label="📥 Baixar Relatório",
                    data=open('relatorio_doacoes.xlsx', 'rb'),
                    file_name="relatorio_doacoes.xlsx",
                    mime="application/vnd.ms-excel"
                )
                
            except Exception as e:
                st.error(f"❌ Erro ao exportar: {e}")

    # Fechar sessão
    session.close()