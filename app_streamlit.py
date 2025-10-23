import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_session, Doador, Receptor, Pet, ItemDoacao, Usuario
from database import hash_senha, gerar_salt, verificar_senha

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
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        border: 1px solid #e0e0e0;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    .info-msg {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #17a2b8;
    }
    .form-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1668a1;
    }
    /* Garantir que a página sempre comece no topo */
    html {
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de autenticação
def inicializar_sessao():
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'num_itens_doacao' not in st.session_state:
        st.session_state.num_itens_doacao = 1
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "Início"
    if 'scroll_position' not in st.session_state:
        st.session_state.scroll_position = 0

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
    st.session_state.num_itens_doacao = 1
    st.session_state.pagina_atual = "Início"

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

# Sidebar
st.sidebar.title("Navegação")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logado como: {st.session_state.usuario_logado}")
    if st.session_state.is_admin:
        st.sidebar.info("Modo Administrador")
    if st.sidebar.button("Sair"):
        fazer_logout()
        st.rerun()
else:
    opcao_login = st.sidebar.radio("Acesso:", ["Entrar", "Cadastrar"])
    
    if opcao_login == "Entrar":
        with st.sidebar:
            st.subheader("Login")
            login = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if fazer_login(login, senha):
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos")
    
    else:
        with st.sidebar:
            st.subheader("Cadastro")
            login = st.text_input("Nome de usuário")
            email = st.text_input("E-mail")
            whatsapp = st.text_input("WhatsApp")
            senha = st.text_input("Senha", type="password")
            if st.button("Cadastrar"):
                sucesso, mensagem = cadastrar_usuario(login, email, whatsapp, senha)
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)

# JavaScript para rolar para o topo quando mudar de página
st.markdown("""
<script>
    // Função para rolar para o topo
    function scrollToTop() {
        window.scrollTo(0, 0);
    }
    
    // Executar quando a página carregar
    window.addEventListener('load', function() {
        scrollToTop();
    });
</script>
""", unsafe_allow_html=True)

# Controle de navegação
if st.session_state.usuario_logado:
    paginas = ["Início", "Cadastrar Doação", "Solicitar Ajuda", "Pets Perdidos", "Visualizar Cadastros"]
    if st.session_state.is_admin:
        paginas.append("Administração")
else:
    paginas = ["Início", "Visualizar Cadastros"]
    st.sidebar.warning("Faça login para cadastrar doações")

# Seleção de página com controle de estado
pagina_selecionada = st.sidebar.selectbox("Selecione a página:", paginas, index=0)

# Verificar se a página mudou
if pagina_selecionada != st.session_state.pagina_atual:
    st.session_state.pagina_atual = pagina_selecionada
    # Forçar rolagem para o topo
    st.markdown("""
    <script>
        window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    st.rerun()

# Páginas principais
if not st.session_state.usuario_logado:
    st.title("Sistema de Doações para Enchentes")
    st.info("Faça login na sidebar para acessar o sistema completo.")
    
else:
    # Sessão do banco
    session = get_session()

    # Página Inicial
    if st.session_state.pagina_atual == "Início":
        st.markdown('<h1 class="main-header">Solidariedade em Tempos de Enchente</h1>', unsafe_allow_html=True)
        
        st.write("""
        ## Juntos somos mais fortes!
        
        Esta plataforma conecta pessoas que querem ajudar com quem precisa de ajuda durante enchentes. 
        Sua solidariedade pode fazer a diferença!
        """)
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_doadores = session.query(Doador).count()
            st.metric("Doadores", total_doadores)
        
        with col2:
            total_itens = session.query(ItemDoacao).count()
            st.metric("Itens", total_itens)
        
        with col3:
            total_receptores = session.query(Receptor).count()
            st.metric("Solicitações", total_receptores)
        
        with col4:
            total_pets = session.query(Pet).count()
            st.metric("Pets", total_pets)

    # Cadastrar Doação
    elif st.session_state.pagina_atual == "Cadastrar Doação":
        st.title("Cadastrar Doação")
        
        with st.form("form_doador"):
            st.subheader("Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                cpf = st.text_input("CPF*", placeholder="000.000.000-00")
                nome = st.text_input("Nome Completo*")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999")
                pode_entregar = st.selectbox("Pode entregar os itens?*", ["", "Sim", "Não"])
            
            st.subheader("Endereço")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000")
                endereco = st.text_input("Endereço*")
                numero = st.text_input("Número*")
            
            with col2:
                bairro = st.text_input("Bairro*")
                cidade = st.text_input("Cidade*")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2)
            
            st.subheader("Itens para Doação")
            num_itens = st.number_input("Quantos itens deseja cadastrar?", min_value=1, max_value=5, value=st.session_state.num_itens_doacao)
            
            itens_data = []
            for i in range(num_itens):
                st.write(f"**Item {i+1}**")
                col1, col2 = st.columns(2)
                
                with col1:
                    item = st.text_input(f"Item*", key=f"item_{i}", 
                                       placeholder="Ex: Arroz, Roupas, Colchão...")
                with col2:
                    quantidade = st.number_input(f"Quantidade*", min_value=1, value=1, key=f"qtd_{i}")
                
                descricao = st.text_area(f"Descrição", key=f"desc_{i}", 
                                       placeholder="Detalhes do item...",
                                       height=60)
                
                itens_data.append({
                    'item': item,
                    'quantidade': quantidade,
                    'descricao': descricao
                })
            
            st.subheader("Disponibilidade")
            prazo_disponibilidade = st.date_input("Prazo de Disponibilidade*", min_value=datetime.today())
            
            submitted = st.form_submit_button("Cadastrar Doação")
            
            if submitted:
                # Validações
                campos_pessoais_ok = all([cpf, nome, telefone, whatsapp, pode_entregar, 
                                        cep, endereco, numero, bairro, cidade, estado])
                
                # Verifica se há pelo menos 1 item preenchido
                itens_validos = [item for item in itens_data if item['item'].strip()]
                if not itens_validos:
                    st.error("Adicione pelo menos um item para doação!")
                    campos_pessoais_ok = False
                
                if campos_pessoais_ok:
                    try:
                        # VERIFICAR SE CPF JÁ EXISTE
                        doador_existente = session.query(Doador).filter(Doador.cpf == cpf).first()
                        if doador_existente:
                            st.error("Já existe um doador cadastrado com este CPF!")
                            st.info(f"CPF {cpf} já pertence a: {doador_existente.nome}")
                        else:
                            # Obter usuário logado
                            usuario_id = st.session_state.user_id
                            
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
                            session.flush()
                            
                            # Cadastra os itens
                            for item_data in itens_validos:
                                novo_item = ItemDoacao(
                                    doador_id=novo_doador.id,
                                    item=item_data['item'],
                                    quantidade=item_data['quantidade'],
                                    descricao=item_data['descricao'].strip() if item_data['descricao'].strip() else None
                                )
                                session.add(novo_item)
                            
                            session.commit()
                            
                            st.success("Doação cadastrada com sucesso!")
                            
                            # Mostra resumo final
                            st.info(f"""
                            **Resumo do cadastro:**
                            - **Doador:** {nome}
                            - **Itens cadastrados:** {len(itens_validos)}
                            - **Quantidade total:** {sum(item['quantidade'] for item in itens_validos)}
                            - **Disponível até:** {prazo_disponibilidade.strftime('%d/%m/%Y')}
                            """)
                            
                    except Exception as e:
                        session.rollback()
                        st.error(f"Erro ao cadastrar doação: {e}")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    # Solicitar Ajuda
    elif st.session_state.pagina_atual == "Solicitar Ajuda":
        st.title("Solicitar Ajuda")
        
        with st.form("form_receptor"):
            st.subheader("Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                cpf = st.text_input("CPF*", placeholder="000.000.000-00")
                nome = st.text_input("Nome Completo*")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999")
                qtde_pessoas = st.number_input("Quantidade de Pessoas*", min_value=1, value=1)
                pode_retirar = st.selectbox("Pode retirar os itens?*", ["", "Sim", "Não"])
            
            st.subheader("Endereço para Entrega")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000")
                endereco = st.text_input("Endereço*")
                numero = st.text_input("Número*")
            
            with col2:
                bairro = st.text_input("Bairro*")
                cidade = st.text_input("Cidade*")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2)
            
            submitted = st.form_submit_button("Solicitar Ajuda")
            
            if submitted:
                campos_ok = all([cpf, nome, telefone, whatsapp, cep, endereco, numero, bairro, cidade, estado, pode_retirar])
                
                if campos_ok:
                    try:
                        # VERIFICAR SE CPF JÁ EXISTE
                        receptor_existente = session.query(Receptor).filter(Receptor.cpf == cpf).first()
                        if receptor_existente:
                            st.error("Já existe uma solicitação cadastrada com este CPF!")
                            st.info(f"CPF {cpf} já pertence a: {receptor_existente.nome}")
                        else:
                            usuario_id = st.session_state.user_id
                            
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
                            
                            st.success("Solicitação de ajuda cadastrada com sucesso!")
                            
                            st.info(f"""
                            **Resumo do cadastro:**
                            - **Solicitante:** {nome}
                            - **Pessoas na família:** {qtde_pessoas}
                            - **Pode retirar:** {pode_retirar}
                            - **Entregar em:** {endereco}, {numero} - {bairro}, {cidade}-{estado}
                            """)
                            
                    except Exception as e:
                        session.rollback()
                        st.error(f"Erro ao cadastrar solicitação: {e}")
                else:
                    st.error("Preencha todos os campos obrigatórios!")

    # Pets Perdidos
    elif st.session_state.pagina_atual == "Pets Perdidos":
        st.title("Pets Perdidos/Encontrados")
        
        tab1, tab2 = st.tabs(["Cadastrar Pet", "Ver Pets"])
        
        with tab1:
            with st.form("form_pet"):
                st.subheader("Dados do Pet")
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
                                       placeholder="Cor, tamanho, características especiais...")
                
                submitted = st.form_submit_button("Cadastrar Pet")
                
                if submitted:
                    campos_ok = all([especie, descricao, local_encontro, contato, situacao])
                    
                    if campos_ok:
                        try:
                            usuario_id = st.session_state.user_id
                            
                            novo_pet = Pet(
                                usuario_id=usuario_id,
                                nome=nome if nome else None,
                                especie=especie,
                                raca=raca if raca else None,
                                descricao=descricao,
                                situacao=situacao,
                                local_encontro=local_encontro,
                                contato=contato
                            )
                            
                            session.add(novo_pet)
                            session.commit()
                            
                            st.success("Pet cadastrado com sucesso!")
                            
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao cadastrar pet: {e}")
                    else:
                        st.error("Preencha todos os campos obrigatórios!")
        
        with tab2:
            st.subheader("Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    st.write(f"**{pet.nome if pet.nome else 'Sem nome'}**")
                    st.write(f"**Espécie:** {pet.especie} | **Raça:** {pet.raca if pet.raca else 'Não informada'}")
                    st.write(f"**Situação:** {pet.situacao} | **Local:** {pet.local_encontro}")
                    st.write(f"**Descrição:** {pet.descricao}")
                    st.write(f"**Contato:** {pet.contato}")
                    st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
                    st.divider()

    # Visualizar Cadastros
    elif st.session_state.pagina_atual == "Visualizar Cadastros":
        st.title("Visualizar Cadastros")
        
        tab1, tab2, tab3 = st.tabs(["Doações", "Solicitações", "Pets"])
        
        with tab1:
            st.subheader("Doações Cadastradas")
            doadores = session.query(Doador).all()
            
            if not doadores:
                st.info("Nenhuma doação cadastrada ainda.")
            else:
                for doador in doadores:
                    with st.expander(f"{doador.nome} - {doador.cidade}/{doador.estado}", expanded=False):
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
                            st.write(f"**Cidade/Estado:** {doador.cidade}/{doador.estado}")
                        
                        if doador.itens:
                            st.write("**Itens para doação:**")
                            for item in doador.itens:
                                st.write(f"• {item.quantidade}x {item.item}" + 
                                       (f" - {item.descricao}" if item.descricao else ""))
        
        with tab2:
            st.subheader("Solicitações de Ajuda")
            receptores = session.query(Receptor).all()
            
            if not receptores:
                st.info("Nenhuma solicitação de ajuda cadastrada ainda.")
            else:
                for receptor in receptores:
                    with st.expander(f"{receptor.nome} - {receptor.cidade}/{receptor.estado}", expanded=False):
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
                            st.write(f"**Cidade/Estado:** {receptor.cidade}/{receptor.estado}")
        
        with tab3:
            st.subheader("Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    with st.expander(f"{pet.nome if pet.nome else 'Sem nome'} - {pet.situacao}", expanded=False):
                        st.write(f"**Espécie:** {pet.especie}")
                        st.write(f"**Raça:** {pet.raca if pet.raca else 'Não informada'}")
                        st.write(f"**Situação:** {pet.situacao}")
                        st.write(f"**Local:** {pet.local_encontro}")
                        st.write(f"**Descrição:** {pet.descricao}")
                        st.write(f"**Contato:** {pet.contato}")
                        st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")

    # Administração
    elif st.session_state.pagina_atual == "Administração":
        st.title("Área Administrativa")
        
        st.subheader("Estatísticas do Sistema")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_usuarios = session.query(Usuario).count()
            st.metric("Total de Usuários", total_usuarios)
        
        with col2:
            total_doadores = session.query(Doador).count()
            st.metric("Doadores", total_doadores)
        
        with col3:
            total_receptores = session.query(Receptor).count()
            st.metric("Solicitantes", total_receptores)
        
        with col4:
            total_pets = session.query(Pet).count()
            st.metric("Pets", total_pets)

    # Fechar sessão
    session.close()