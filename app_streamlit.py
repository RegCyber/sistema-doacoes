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

# CSS personalizado com melhorias de acessibilidade
def aplicar_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* Variáveis de Cores - Contraste aprimorado para acessibilidade */
:root {
    --primary-color: #B43D1F; 
    --secondary-color: #dc3545; 
    --background-light: #f8f9fa; 
    --surface-white: #ffffff; 
    --text-dark: #212529; /* Contraste aumentado */
    --text-medium: #495057; /* Contraste aumentado */
    --success-color: #28a745; 
    --error-color: #dc3545; 
    --info-color: #ffc107; 
    --border-color: #e9ecef; 
    --shadow-subtle: 0 4px 12px rgba(0, 0, 0, 0.05);
    --focus-color: #0056b3; /* Cor para foco do teclado */
}

body {
    font-family: 'Poppins', sans-serif; 
    background-color: var(--background-light);
    color: var(--text-dark);
    line-height: 1.6; /* Melhor legibilidade */
}

.main-header {
    font-size: 2.8rem;
    color: var(--primary-color);
    text-align: left; 
    margin-bottom: 1.5rem;
    margin-top: 0.5rem;
    font-weight: 700; 
    border-bottom: 3px solid var(--secondary-color); 
    padding-bottom: 0.5rem;
}

/* Melhorias de acessibilidade para cartões de métrica */
.metric-card {
    background-color: var(--surface-white);
    padding: 1.5rem;
    border-radius: 12px; 
    text-align: left; 
    margin: 0.75rem 0; 
    border: none; 
    box-shadow: var(--shadow-subtle); 
    transition: transform 0.2s ease-in-out;
    height: 100%; 
}

.metric-card:hover {
    transform: translateY(-5px); 
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.metric-card h3 {
    font-size: 0.9rem;
    color: var(--text-medium);
    margin-bottom: 0.5rem;
    font-weight: 400;
    letter-spacing: 0.5px;
    text-transform: uppercase; 
}

.metric-card h2 {
    font-size: 2.5rem; 
    color: var(--primary-color); 
    margin: 0.2rem 0 0 0;
    font-weight: 700;
}

/* Mensagens de Status com contraste aprimorado */
.success-msg, .error-msg, .info-msg {
    padding: 1.2rem;
    border-radius: 8px;
    margin: 1.5rem 0;
    border-left: 6px solid; 
    font-weight: 400;
    line-height: 1.5;
}

.success-msg {
    background-color: #d4edda;
    color: #155724;
    border-left-color: var(--success-color);
}

.error-msg {
    background-color: #f8d7da;
    color: #721c24;
    border-left-color: var(--error-color);
}

.info-msg {
    background-color: #fff3cd;
    color: #856404;
    border-left-color: var(--info-color);
}

/* Seção de Formulário com melhor acessibilidade */
.form-section {
    background: var(--surface-white);
    padding: 2rem;
    border-radius: 12px;
    margin: 1.5rem 0;
    border: none;
    box-shadow: var(--shadow-subtle);
}

/* Botões Streamlit com foco visível para navegação por teclado */
.stButton button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem; 
    border-radius: 8px; 
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 6px rgba(180, 61, 31, 0.2); 
    width: 100%; 
}

.stButton button:hover {
    background-color: #8D2F17; 
    transform: translateY(-2px); 
    box-shadow: 0 6px 10px rgba(180, 61, 31, 0.3);
}

/* Foco visível para acessibilidade de teclado */
.stButton button:focus {
    outline: 3px solid var(--focus-color);
    outline-offset: 2px;
}

/* Melhorias de acessibilidade para inputs */
.stTextInput input:focus, 
.stTextArea textarea:focus,
.stSelectbox select:focus {
    outline: 2px solid var(--focus-color);
    outline-offset: 1px;
}

/* Estilo para o st.metric */
div[data-testid="stMetric"] > div:nth-child(1) {
    padding: 0;
}
div[data-testid="stMetric"] > div:nth-child(1) > div:nth-child(1) {
    margin: 0;
}
div[data-testid="stMetric"] > div:nth-child(2) {
    padding: 0;
    margin: 0;
}

/* Menu de navegação com melhor acessibilidade */
.sidebar-nav {
    margin-top: 2rem;
}
.sidebar-nav-item {
    padding: 0.75rem 1rem;
    margin: 0.25rem 0;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sidebar-nav-item:hover {
    background-color: rgba(180, 61, 31, 0.1);
}
.sidebar-nav-item.active {
    background-color: var(--primary-color);
    color: white;
}

/* Classes para acessibilidade de leitores de tela */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* Indicadores de status para leitores de tela */
.aria-live-region {
    position: absolute;
    left: -10000px;
    width: 1px;
    height: 1px;
    overflow: hidden;
}

</style>
             """, unsafe_allow_html=True)

aplicar_css()

# Sistema de autenticação
def inicializar_sessao():
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_cpf' not in st.session_state:
        st.session_state.user_cpf = None
    if 'itens_doacao' not in st.session_state:
        st.session_state.itens_doacao = [{'item': '', 'quantidade': 1, 'descricao': ''}]
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "Início"
    if 'cpf_verificado_doador' not in st.session_state:
        st.session_state.cpf_verificado_doador = False
    if 'cpf_verificado_receptor' not in st.session_state:
        st.session_state.cpf_verificado_receptor = False
    if 'edicao_ativa' not in st.session_state:
        st.session_state.edicao_ativa = None

def fazer_login(login, senha):
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.login == login).first()
        if usuario and verificar_senha(senha, usuario.salt, usuario.senha_hash):
            st.session_state.usuario_logado = usuario.login
            st.session_state.is_admin = usuario.is_admin
            st.session_state.user_id = usuario.id
            st.session_state.user_cpf = usuario.cpf
            return True
        return False
    finally:
        session.close()

def fazer_logout():
    st.session_state.usuario_logado = None
    st.session_state.is_admin = False
    st.session_state.user_id = None
    st.session_state.user_cpf = None
    st.session_state.itens_doacao = [{'item': '', 'quantidade': 1, 'descricao': ''}]
    st.session_state.pagina_atual = "Início"
    st.session_state.cpf_verificado_doador = False
    st.session_state.cpf_verificado_receptor = False
    st.session_state.edicao_ativa = None

def cadastrar_usuario(login, email, whatsapp, senha, cpf):
    session = get_session()
    try:
        # Verificar se usuário já existe
        existe = session.query(Usuario).filter(Usuario.login == login).first()
        if existe:
            return False, "Usuário já existe"
        
        # Verificar se CPF já existe
        existe_cpf = session.query(Usuario).filter(Usuario.cpf == cpf).first()
        if existe_cpf:
            return False, "CPF já cadastrado"
        
        if len(senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres"
        
        if not validar_cpf(cpf):
            return False, "CPF inválido"
        
        salt = gerar_salt()
        senha_hash = hash_senha(senha, salt)
        
        # Definir como admin se for o CPF especial
        is_admin = (cpf == "00000000001")
        
        novo_usuario = Usuario(
            login=login,
            email=email,
            whatsapp=whatsapp,
            senha_hash=senha_hash,
            salt=salt,
            cpf=cpf,
            is_admin=is_admin
        )
        
        session.add(novo_usuario)
        session.commit()
        return True, "Usuário cadastrado com sucesso!"
        
    except Exception as e:
        session.rollback()
        return False, f"Erro ao cadastrar: {e}"
    finally:
        session.close()

def verificar_cpf_existente(cpf, tipo):
    """Verifica se CPF já existe no sistema"""
    session = get_session()
    try:
        if tipo == "doador":
            existe = session.query(Doador).filter(Doador.cpf == cpf).first()
        else:  # receptor
            existe = session.query(Receptor).filter(Receptor.cpf == cpf).first()
        return existe is not None
    finally:
        session.close()

def formatar_cpf(cpf):
    """Remove formatação do CPF para verificação"""
    return ''.join(filter(str.isdigit, cpf))

def validar_cpf(cpf):
    """Validação básica de CPF"""
    cpf_limpo = formatar_cpf(cpf)
    return len(cpf_limpo) == 11

def usuario_tem_permissao(registro):
    """Verifica se usuário tem permissão para editar/excluir registro"""
    if st.session_state.is_admin:
        return True
    # Verificar se o usuário é dono do registro pelo CPF
    if hasattr(registro, 'cpf') and registro.cpf == st.session_state.user_cpf:
        return True
    # Verificar se o usuário é dono pelo usuario_id
    if hasattr(registro, 'usuario_id') and registro.usuario_id == st.session_state.user_id:
        return True
    return False

def usuario_pode_editar_por_cpf(cpf_registro):
    """Verifica se usuário pode editar registro baseado no CPF"""
    if st.session_state.is_admin:
        return True
    return cpf_registro == st.session_state.user_cpf

# Inicializar sessão
inicializar_sessao()

# Sidebar com melhorias de acessibilidade
st.sidebar.title("Login ou Cadastro")

# Região ARIA Live para anunciar mudanças dinâmicas
st.markdown('<div class="aria-live-region" aria-live="polite" aria-atomic="true"></div>', unsafe_allow_html=True)

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logado como: {st.session_state.usuario_logado}")
    if st.session_state.is_admin:
        st.sidebar.info("Modo Administrador")
    
    if st.sidebar.button("Sair", key="logout_btn"):
        fazer_logout()
        st.rerun()
    
    # Menu de navegação com atributos ARIA
    st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    st.sidebar.subheader("Navegação")
    
    paginas = {
        "Início": "🏠", 
        "Cadastrar Doação": "🎁", 
        "Solicitar Ajuda": "🆘", 
        "Pets Perdidos": "🐾", 
        "Visualizar Cadastros": "👀"
    }
    
    if st.session_state.is_admin:
        paginas["Administração"] = "⚡"
    
    for pagina_nome, emoji in paginas.items():
        if st.sidebar.button(f"{emoji} {pagina_nome}", key=f"nav_{pagina_nome}", use_container_width=True):
            st.session_state.pagina_atual = pagina_nome
            st.rerun()
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
else:
    opcao_login = st.sidebar.radio("Acesso:", ["Entrar", "Cadastrar"], key="acesso_radio")
    
    if opcao_login == "Entrar":
        with st.sidebar:
            st.subheader("Login")
            login = st.text_input("Usuário", key="login_input", 
                                 help="Digite seu nome de usuário")
            senha = st.text_input("Senha", type="password", key="senha_input",
                                 help="Digite sua senha")
            if st.button("Entrar", key="login_btn"):
                if login and senha:
                    if fazer_login(login, senha):
                        st.success("Login realizado!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos")
                else:
                    st.error("Preencha usuário e senha")
    
    else:
        with st.sidebar:
            st.subheader("Cadastro")
            # Usar keys únicas para evitar conflitos
            login = st.text_input("Nome de usuário", key="cad_login",
                                 help="Escolha um nome de usuário único")
            email = st.text_input("E-mail", key="cad_email",
                                 help="Digite seu e-mail válido")
            whatsapp = st.text_input("WhatsApp", key="cad_whatsapp",
                                    help="Digite seu número com DDD")
            cpf = st.text_input("CPF*", key="cad_cpf",
                               help="Digite seu CPF (será usado para vincular seus cadastros)")
            senha = st.text_input("Senha", type="password", key="cad_senha",
                                 help="Mínimo de 6 caracteres")
            
            if st.button("Cadastrar", key="cad_btn"):
                if login and email and whatsapp and senha and cpf:
                    if validar_cpf(cpf):
                        sucesso, mensagem = cadastrar_usuario(login, email, whatsapp, senha, formatar_cpf(cpf))
                        if sucesso:
                            st.success(mensagem)
                            # Mudar para a aba de login após cadastro bem-sucedido
                            st.session_state.acesso_radio = "Entrar"
                            st.rerun()
                        else:
                            st.error(mensagem)
                    else:
                        st.error("CPF inválido")
                else:
                    st.error("Preencha todos os campos")

# JavaScript para acessibilidade - rolar para o topo e anunciar mudanças
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
    
    // Melhorar navegação por teclado
    document.addEventListener('keydown', function(e) {
        // Fechar modais com ESC
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('[role="dialog"]');
            modals.forEach(modal => {
                if (modal.style.display !== 'none') {
                    modal.style.display = 'none';
                }
            });
        }
    });
    
    // Anunciar mudanças de página para leitores de tela
    function announcePageChange(pageName) {
        const liveRegion = document.querySelector('.aria-live-region');
        if (liveRegion) {
            liveRegion.textContent = 'Página carregada: ' + pageName;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
</script>
""", unsafe_allow_html=True)

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
            st.markdown(f'<div class="metric-card"><h3>👥 Doadores</h3><h2>{total_doadores}</h2></div>', unsafe_allow_html=True)
        
        with col2:
            total_itens = session.query(ItemDoacao).count()
            st.markdown(f'<div class="metric-card"><h3>📦 Itens</h3><h2>{total_itens}</h2></div>', unsafe_allow_html=True)
        
        with col3:
            total_receptores = session.query(Receptor).count()
            st.markdown(f'<div class="metric-card"><h3>🆘 Solicitações</h3><h2>{total_receptores}</h2></div>', unsafe_allow_html=True)
        
        with col4:
            total_pets = session.query(Pet).count()
            st.markdown(f'<div class="metric-card"><h3>🐾 Pets</h3><h2>{total_pets}</h2></div>', unsafe_allow_html=True)

    # Cadastrar Doação - COM VÍNCULO DE CPF E SEÇÃO DE ITENS NO FINAL
    elif st.session_state.pagina_atual == "Cadastrar Doação":
        st.markdown('<h1 class="main-header">Cadastrar Doação</h1>', unsafe_allow_html=True)
        
        # Verificar se está em modo de edição
        doador_editando = None
        if st.session_state.edicao_ativa and st.session_state.edicao_ativa.startswith("doador_"):
            doador_id = int(st.session_state.edicao_ativa.split("_")[1])
            doador_editando = session.query(Doador).filter(Doador.id == doador_id).first()
            
            if doador_editando and not usuario_tem_permissao(doador_editando):
                st.error("Você não tem permissão para editar esta doação.")
                st.session_state.edicao_ativa = None
                doador_editando = None
        
        # FORMULÁRIO PRINCIPAL (dados do doador)
        with st.form("form_doador"):
            st.subheader("Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                # Campo CPF - se estiver editando, mostra como texto
                if doador_editando:
                    st.text_input("CPF*", value=doador_editando.cpf, disabled=True)
                    cpf = doador_editando.cpf
                    st.session_state.cpf_verificado_doador = True
                else:
                    cpf = st.text_input("CPF*", placeholder="000.000.000-00", key="cpf_doador",
                                      value=st.session_state.user_cpf if st.session_state.user_cpf else "")
                    # Verificação imediata do CPF
                    if cpf and validar_cpf(cpf):
                        cpf_formatado = formatar_cpf(cpf)
                        # Verificar se o CPF pertence ao usuário logado ou se é admin
                        if cpf_formatado != st.session_state.user_cpf and not st.session_state.is_admin:
                            st.error("❌ Este CPF não pertence ao seu usuário!")
                            st.session_state.cpf_verificado_doador = False
                        elif verificar_cpf_existente(cpf_formatado, "doador"):
                            st.error("❌ CPF já cadastrado no sistema!")
                            st.session_state.cpf_verificado_doador = False
                        else:
                            st.success("✅ CPF disponível para cadastro")
                            st.session_state.cpf_verificado_doador = True
                    elif cpf and not validar_cpf(cpf):
                        st.error("❌ CPF inválido")
                        st.session_state.cpf_verificado_doador = False
                
                nome = st.text_input("Nome Completo*", 
                                   value=doador_editando.nome if doador_editando else "")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999",
                                       value=doador_editando.telefone if doador_editando else "")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999",
                                       value=doador_editando.whatsapp if doador_editando else "")
                pode_entregar = st.selectbox("Pode entregar os itens?*", ["", "Sim", "Não"],
                                           index=1 if doador_editando and doador_editando.pode_entregar else 0,
                                           key="pode_entregar")
            
            st.subheader("Endereço")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000",
                                  value=doador_editando.cep if doador_editando else "")
                endereco = st.text_input("Endereço*",
                                       value=doador_editando.endereco if doador_editando else "")
                numero = st.text_input("Número*",
                                     value=doador_editando.numero if doador_editando else "")
            
            with col2:
                bairro = st.text_input("Bairro*",
                                     value=doador_editando.bairro if doador_editando else "")
                cidade = st.text_input("Cidade*",
                                     value=doador_editando.cidade if doador_editando else "")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2,
                                     value=doador_editando.estado if doador_editando else "")
            
            st.subheader("Disponibilidade")
            prazo_disponibilidade = st.date_input("Prazo de Disponibilidade*", 
                                               min_value=datetime.today(),
                                               value=doador_editando.prazo_disponibilidade if doador_editando else datetime.today())
            
            # Botão de submit dentro do formulário
            if doador_editando:
                submitted = st.form_submit_button("💾 Atualizar Doação")
            else:
                submitted = st.form_submit_button("Cadastrar Doação")
        
        # SEÇÃO DE ITENS PARA DOAÇÃO (FORA DO FORMULÁRIO, APÓS OS DADOS BÁSICOS)
        st.subheader("Itens para Doação")
        
        # Carregar itens existentes se estiver editando
        if doador_editando and not st.session_state.itens_doacao[0]['item']:
            st.session_state.itens_doacao = []
            for item in doador_editando.itens:
                st.session_state.itens_doacao.append({
                    'item': item.item,
                    'quantidade': item.quantidade,
                    'descricao': item.descricao or ''
                })
        
        st.write(f"**Cadastrando {len(st.session_state.itens_doacao)} item(s)**")
        
        # Botão para adicionar item (FORA DO FORMULÁRIO)
        if st.button("➕ Acrescentar Item", key="add_item_btn"):
            st.session_state.itens_doacao.append({'item': '', 'quantidade': 1, 'descricao': ''})
            st.rerun()
        
        # Renderizar itens existentes (FORA DO FORMULÁRIO)
        itens_para_remover = []
        for i, item_data in enumerate(st.session_state.itens_doacao):
            st.write(f"**Item {i+1}**")
            col1, col2 = st.columns(2)
            
            with col1:
                item = st.text_input(
                    f"Item*", 
                    value=item_data['item'],
                    key=f"item_{i}", 
                    placeholder="Ex: Arroz, Roupas, Colchão..."
                )
            with col2:
                quantidade = st.number_input(
                    f"Quantidade*", 
                    min_value=1, 
                    value=item_data['quantidade'],
                    key=f"qtd_{i}"
                )
            
            descricao = st.text_area(
                f"Descrição", 
                value=item_data['descricao'],
                key=f"desc_{i}", 
                placeholder="Detalhes do item...",
                height=60
            )
            
            # Atualizar dados na session state
            st.session_state.itens_doacao[i] = {
                'item': item,
                'quantidade': quantidade,
                'descricao': descricao
            }
            
            # Botão para remover item (FORA DO FORMULÁRIO, em coluna separada)
            if len(st.session_state.itens_doacao) > 1:
                col_remove, _ = st.columns([1, 5])
                with col_remove:
                    if st.button(f"❌ Remover Item {i+1}", key=f"remove_{i}"):
                        itens_para_remover.append(i)
            
            # Adicionar divisória entre itens (exceto no último)
            if i < len(st.session_state.itens_doacao) - 1:
                st.divider()
        
        # Processar remoção de itens após o loop
        if itens_para_remover:
            # Remover em ordem decrescente para evitar problemas de índice
            for i in sorted(itens_para_remover, reverse=True):
                if len(st.session_state.itens_doacao) > 1:
                    st.session_state.itens_doacao.pop(i)
            st.rerun()
        
        # Processar o envio do formulário
        if submitted:
            # Validações
            campos_pessoais_ok = all([cpf, nome, telefone, whatsapp, pode_entregar, 
                                    cep, endereco, numero, bairro, cidade, estado])
            
            # Verificar CPF (apenas para novo cadastro)
            if not doador_editando and cpf and not st.session_state.cpf_verificado_doador:
                st.error("Verifique o CPF antes de continuar!")
                campos_pessoais_ok = False
            
            # Verifica se há pelo menos 1 item preenchido
            itens_validos = [item for item in st.session_state.itens_doacao if item['item'].strip()]
            if not itens_validos:
                st.error("Adicione pelo menos um item para doação!")
                campos_pessoais_ok = False
            
            if campos_pessoais_ok:
                try:
                    if doador_editando:
                        # ATUALIZAR DOAÇÃO EXISTENTE
                        # Verificar permissão
                        if not usuario_tem_permissao(doador_editando):
                            st.error("Você não tem permissão para editar esta doação.")
                        else:
                            # Atualizar dados do doador
                            doador_editando.nome = nome
                            doador_editando.endereco = endereco
                            doador_editando.numero = numero
                            doador_editando.cep = cep
                            doador_editando.bairro = bairro
                            doador_editando.cidade = cidade
                            doador_editando.estado = estado
                            doador_editando.telefone = telefone
                            doador_editando.whatsapp = whatsapp
                            doador_editando.pode_entregar = pode_entregar == "Sim"
                            doador_editando.prazo_disponibilidade = prazo_disponibilidade
                            
                            # Remover itens antigos
                            for item in doador_editando.itens:
                                session.delete(item)
                            
                            # Adicionar novos itens
                            for item_data in itens_validos:
                                novo_item = ItemDoacao(
                                    doador_id=doador_editando.id,
                                    item=item_data['item'],
                                    quantidade=item_data['quantidade'],
                                    descricao=item_data['descricao'].strip() if item_data['descricao'].strip() else None
                                )
                                session.add(novo_item)
                            
                            session.commit()
                            
                            st.success("Doação atualizada com sucesso!")
                            st.session_state.edicao_ativa = None
                            st.session_state.itens_doacao = [{'item': '', 'quantidade': 1, 'descricao': ''}]
                            
                    else:
                        # NOVA DOAÇÃO
                        # VERIFICAR SE CPF JÁ EXISTE (verificação final)
                        cpf_formatado = formatar_cpf(cpf)
                        doador_existente = session.query(Doador).filter(Doador.cpf == cpf_formatado).first()
                        if doador_existente:
                            st.error("Já existe um doador cadastrado com este CPF!")
                            st.info(f"CPF {cpf} já pertence a: {doador_existente.nome}")
                        else:
                            # Obter usuário logado
                            usuario_id = st.session_state.user_id
                            
                            # Cadastra o doador
                            novo_doador = Doador(
                                usuario_id=usuario_id,
                                cpf=cpf_formatado,
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
                            
                            # Limpa os itens após cadastro bem-sucedido
                            st.session_state.itens_doacao = [{'item': '', 'quantidade': 1, 'descricao': ''}]
                            
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro ao cadastrar doação: {e}")
            else:
                st.error("Preencha todos os campos obrigatórios!")
        
        # Botão para cancelar edição (FORA DO FORMULÁRIO)
        if doador_editando:
            if st.button("❌ Cancelar Edição", key="cancel_edit"):
                st.session_state.edicao_ativa = None
                st.session_state.itens_doacao = [{'item': '', 'quantidade': 1, 'descricao': ''}]
                st.rerun()

    # Solicitar Ajuda - COM VÍNCULO DE CPF
    elif st.session_state.pagina_atual == "Solicitar Ajuda":
        st.markdown('<h1 class="main-header">Solicitar Ajuda</h1>', unsafe_allow_html=True)
        
        # Verificar se está em modo de edição
        receptor_editando = None
        if st.session_state.edicao_ativa and st.session_state.edicao_ativa.startswith("receptor_"):
            receptor_id = int(st.session_state.edicao_ativa.split("_")[1])
            receptor_editando = session.query(Receptor).filter(Receptor.id == receptor_id).first()
            
            if receptor_editando and not usuario_tem_permissao(receptor_editando):
                st.error("Você não tem permissão para editar esta solicitação.")
                st.session_state.edicao_ativa = None
                receptor_editando = None
        
        with st.form("form_receptor"):
            st.subheader("Dados Pessoais")
            col1, col2 = st.columns(2)
            
            with col1:
                # Campo CPF - se estiver editando, mostra como texto
                if receptor_editando:
                    st.text_input("CPF*", value=receptor_editando.cpf, disabled=True)
                    cpf = receptor_editando.cpf
                    st.session_state.cpf_verificado_receptor = True
                else:
                    cpf = st.text_input("CPF*", placeholder="000.000.000-00", key="cpf_receptor",
                                      value=st.session_state.user_cpf if st.session_state.user_cpf else "")
                    # Verificação imediata do CPF
                    if cpf and validar_cpf(cpf):
                        cpf_formatado = formatar_cpf(cpf)
                        # Verificar se o CPF pertence ao usuário logado ou se é admin
                        if cpf_formatado != st.session_state.user_cpf and not st.session_state.is_admin:
                            st.error("❌ Este CPF não pertence ao seu usuário!")
                            st.session_state.cpf_verificado_receptor = False
                        elif verificar_cpf_existente(cpf_formatado, "receptor"):
                            st.error("❌ CPF já cadastrado no sistema!")
                            st.session_state.cpf_verificado_receptor = False
                        else:
                            st.success("✅ CPF disponível para cadastro")
                            st.session_state.cpf_verificado_receptor = True
                    elif cpf and not validar_cpf(cpf):
                        st.error("❌ CPF inválido")
                        st.session_state.cpf_verificado_receptor = False
                    
                nome = st.text_input("Nome Completo*", 
                                   value=receptor_editando.nome if receptor_editando else "")
                telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999",
                                       value=receptor_editando.telefone if receptor_editando else "")
            
            with col2:
                whatsapp = st.text_input("WhatsApp*", placeholder="(11) 99999-9999",
                                       value=receptor_editando.whatsapp if receptor_editando else "")
                qtde_pessoas = st.number_input("Quantidade de Pessoas*", min_value=1, 
                                             value=receptor_editando.qtde_pessoas if receptor_editando else 1)
                pode_retirar = st.selectbox("Pode retirar os itens?*", ["", "Sim", "Não"],
                                          index=1 if receptor_editando and receptor_editando.pode_retirar else 0)
            
            st.subheader("Endereço para Entrega")
            col1, col2 = st.columns(2)
            
            with col1:
                cep = st.text_input("CEP*", placeholder="00000-000",
                                  value=receptor_editando.cep if receptor_editando else "")
                endereco = st.text_input("Endereço*",
                                       value=receptor_editando.endereco if receptor_editando else "")
                numero = st.text_input("Número*",
                                     value=receptor_editando.numero if receptor_editando else "")
            
            with col2:
                bairro = st.text_input("Bairro*",
                                     value=receptor_editando.bairro if receptor_editando else "")
                cidade = st.text_input("Cidade*",
                                     value=receptor_editando.cidade if receptor_editando else "")
                estado = st.text_input("Estado*", placeholder="SP", max_chars=2,
                                     value=receptor_editando.estado if receptor_editando else "")
            
            if receptor_editando:
                submitted = st.form_submit_button("💾 Atualizar Solicitação")
            else:
                submitted = st.form_submit_button("Solicitar Ajuda")
            
            if submitted:
                campos_ok = all([cpf, nome, telefone, whatsapp, cep, endereco, numero, bairro, cidade, estado, pode_retirar])
                
                # Verificar CPF (apenas para novo cadastro)
                if not receptor_editando and cpf and not st.session_state.cpf_verificado_receptor:
                    st.error("Verifique o CPF antes de continuar!")
                    campos_ok = False
                
                if campos_ok:
                    try:
                        if receptor_editando:
                            # ATUALIZAR SOLICITAÇÃO EXISTENTE
                            # Verificar permissão
                            if not usuario_tem_permissao(receptor_editando):
                                st.error("Você não tem permissão para editar esta solicitação.")
                            else:
                                receptor_editando.nome = nome
                                receptor_editando.endereco = endereco
                                receptor_editando.numero = numero
                                receptor_editando.cep = cep
                                receptor_editando.bairro = bairro
                                receptor_editando.cidade = cidade
                                receptor_editando.estado = estado
                                receptor_editando.telefone = telefone
                                receptor_editando.whatsapp = whatsapp
                                receptor_editando.qtde_pessoas = qtde_pessoas
                                receptor_editando.pode_retirar = pode_retirar == "Sim"
                                
                                session.commit()
                                
                                st.success("Solicitação atualizada com sucesso!")
                                st.session_state.edicao_ativa = None
                                
                        else:
                            # NOVA SOLICITAÇÃO
                            # VERIFICAR SE CPF JÁ EXISTE (verificação final)
                            cpf_formatado = formatar_cpf(cpf)
                            receptor_existente = session.query(Receptor).filter(Receptor.cpf == cpf_formatado).first()
                            if receptor_existente:
                                st.error("Já existe uma solicitação cadastrada com este CPF!")
                                st.info(f"CPF {cpf} já pertence a: {receptor_existente.nome}")
                            else:
                                usuario_id = st.session_state.user_id
                                
                                novo_receptor = Receptor(
                                    usuario_id=usuario_id,
                                    cpf=cpf_formatado,
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
        
        # Botão para cancelar edição (FORA DO FORMULÁRIO)
        if receptor_editando:
            if st.button("❌ Cancelar Edição", key="cancel_edit_receptor"):
                st.session_state.edicao_ativa = None
                st.rerun()

    # Pets Perdidos - COM VÍNCULO DE CPF
    elif st.session_state.pagina_atual == "Pets Perdidos":
        st.markdown('<h1 class="main-header">Pets Perdidos/Encontrados</h1>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Cadastrar/Editar Pet", "Ver Pets"])
        
        with tab1:
            # Verificar se está em modo de edição
            pet_editando = None
            if st.session_state.edicao_ativa and st.session_state.edicao_ativa.startswith("pet_"):
                pet_id = int(st.session_state.edicao_ativa.split("_")[1])
                pet_editando = session.query(Pet).filter(Pet.id == pet_id).first()
                
                if pet_editando and not usuario_tem_permissao(pet_editando):
                    st.error("Você não tem permissão para editar este pet.")
                    st.session_state.edicao_ativa = None
                    pet_editando = None
            
            with st.form("form_pet"):
                st.subheader("Dados do Pet")
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome do Pet", placeholder="Opcional",
                                       value=pet_editando.nome if pet_editando else "")
                    especie = st.selectbox("Espécie*", ["", "Cachorro", "Gato", "Ave", "Outro"],
                                         index=["", "Cachorro", "Gato", "Ave", "Outro"].index(
                                             pet_editando.especie if pet_editando else ""))
                    raca = st.text_input("Raça", placeholder="Opcional",
                                       value=pet_editando.raca if pet_editando else "")
                
                with col2:
                    situacao = st.selectbox("Situação*", ["", "Perdido", "Encontrado", "Para Adoção"],
                                          index=["", "Perdido", "Encontrado", "Para Adoção"].index(
                                              pet_editando.situacao if pet_editando else ""))
                    local_encontro = st.text_input("Local onde foi encontrado/perdido*",
                                                 value=pet_editando.local_encontro if pet_editando else "")
                    contato = st.text_input("Contato para informações*", placeholder="Telefone/WhatsApp",
                                          value=pet_editando.contato if pet_editando else "")
                
                descricao = st.text_area("Descrição do Pet*", 
                                       placeholder="Cor, tamanho, características especiais...",
                                       value=pet_editando.descricao if pet_editando else "")
                
                if pet_editando:
                    submitted = st.form_submit_button("💾 Atualizar Pet")
                else:
                    submitted = st.form_submit_button("Cadastrar Pet")
                
                if submitted:
                    campos_ok = all([especie, descricao, local_encontro, contato, situacao])
                    
                    if campos_ok:
                        try:
                            if pet_editando:
                                # ATUALIZAR PET EXISTENTE
                                # Verificar permissão
                                if not usuario_tem_permissao(pet_editando):
                                    st.error("Você não tem permissão para editar este pet.")
                                else:
                                    pet_editando.nome = nome if nome else None
                                    pet_editando.especie = especie
                                    pet_editando.raca = raca if raca else None
                                    pet_editando.descricao = descricao
                                    pet_editando.situacao = situacao
                                    pet_editando.local_encontro = local_encontro
                                    pet_editando.contato = contato
                                    
                                    session.commit()
                                    
                                    st.success("Pet atualizado com sucesso!")
                                    st.session_state.edicao_ativa = None
                                    
                            else:
                                # NOVO PET
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
            
            # Botão para cancelar edição (FORA DO FORMULÁRIO)
            if pet_editando:
                if st.button("❌ Cancelar Edição", key="cancel_edit_pet"):
                    st.session_state.edicao_ativa = None
                    st.rerun()
        
        with tab2:
            st.subheader("Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    with st.expander(f"{pet.nome if pet.nome else 'Sem nome'} - {pet.situacao}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Espécie:** {pet.especie}")
                            st.write(f"**Raça:** {pet.raca if pet.raca else 'Não informada'}")
                            st.write(f"**Situação:** {pet.situacao}")
                            st.write(f"**Local:** {pet.local_encontro}")
                        
                        with col2:
                            st.write(f"**Descrição:** {pet.descricao}")
                            st.write(f"**Contato:** {pet.contato}")
                            st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
                            st.write(f"**Cadastrado por:** {pet.usuario.login} (CPF: {pet.usuario.cpf})")
                        
                        # Botões de ação - apenas para usuário que criou ou admin
                        if usuario_tem_permissao(pet):
                            col_edit, col_del = st.columns(2)
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_pet_{pet.id}"):
                                    st.session_state.edicao_ativa = f"pet_{pet.id}"
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ Excluir", key=f"del_pet_{pet.id}"):
                                    session.delete(pet)
                                    session.commit()
                                    st.success("Pet excluído com sucesso!")
                                    st.rerun()
                        
                        st.divider()

    # Visualizar Cadastros - COM VÍNCULO DE CPF
    elif st.session_state.pagina_atual == "Visualizar Cadastros":
        st.markdown('<h1 class="main-header">Visualizar Cadastros</h1>', unsafe_allow_html=True)
        
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
                            st.write(f"**Cadastrado por:** {doador.usuario.login} (CPF: {doador.usuario.cpf})")
                        
                        if doador.itens:
                            st.write("**Itens para doação:**")
                            for item in doador.itens:
                                st.write(f"• {item.quantidade}x {item.item}" + 
                                       (f" - {item.descricao}" if item.descricao else ""))
                        
                        # Botões de ação - apenas para usuário que criou ou admin
                        if usuario_tem_permissao(doador):
                            col_edit, col_del = st.columns(2)
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_doador_{doador.id}"):
                                    st.session_state.edicao_ativa = f"doador_{doador.id}"
                                    st.session_state.pagina_atual = "Cadastrar Doação"
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ Excluir", key=f"del_doador_{doador.id}"):
                                    # Excluir itens primeiro
                                    for item in doador.itens:
                                        session.delete(item)
                                    session.delete(doador)
                                    session.commit()
                                    st.success("Doação excluída com sucesso!")
                                    st.rerun()
        
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
                            st.write(f"**Cadastrado por:** {receptor.usuario.login} (CPF: {receptor.usuario.cpf})")
                        
                        # Botões de ação - apenas para usuário que criou ou admin
                        if usuario_tem_permissao(receptor):
                            col_edit, col_del = st.columns(2)
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_receptor_{receptor.id}"):
                                    st.session_state.edicao_ativa = f"receptor_{receptor.id}"
                                    st.session_state.pagina_atual = "Solicitar Ajuda"
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ Excluir", key=f"del_receptor_{receptor.id}"):
                                    session.delete(receptor)
                                    session.commit()
                                    st.success("Solicitação excluída com sucesso!")
                                    st.rerun()
        
        with tab3:
            st.subheader("Pets Cadastrados")
            pets = session.query(Pet).all()
            
            if not pets:
                st.info("Nenhum pet cadastrado ainda.")
            else:
                for pet in pets:
                    with st.expander(f"{pet.nome if pet.nome else 'Sem nome'} - {pet.situacao}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Espécie:** {pet.especie}")
                            st.write(f"**Raça:** {pet.raca if pet.raca else 'Não informada'}")
                            st.write(f"**Situação:** {pet.situacao}")
                            st.write(f"**Local:** {pet.local_encontro}")
                        
                        with col2:
                            st.write(f"**Descrição:** {pet.descricao}")
                            st.write(f"**Contato:** {pet.contato}")
                            st.write(f"**Cadastrado em:** {pet.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
                            st.write(f"**Cadastrado por:** {pet.usuario.login} (CPF: {pet.usuario.cpf})")
                        
                        # Botões de ação - apenas para usuário que criou ou admin
                        if usuario_tem_permissao(pet):
                            col_edit, col_del = st.columns(2)
                            
                            with col_edit:
                                if st.button("✏️ Editar", key=f"edit_pet_{pet.id}"):
                                    st.session_state.edicao_ativa = f"pet_{pet.id}"
                                    st.session_state.pagina_atual = "Pets Perdidos"
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ Excluir", key=f"del_pet_{pet.id}"):
                                    session.delete(pet)
                                    session.commit()
                                    st.success("Pet excluído com sucesso!")
                                    st.rerun()

    # Administração
    elif st.session_state.pagina_atual == "Administração":
        st.markdown('<h1 class="main-header">Área Administrativa</h1>', unsafe_allow_html=True)
        
        if not st.session_state.is_admin:
            st.error("Acesso negado. Apenas administradores podem acessar esta página.")
        else:
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
            
            st.subheader("Gerenciamento de Usuários")
            usuarios = session.query(Usuario).all()
            
            for usuario in usuarios:
                with st.expander(f"Usuário: {usuario.login} - Admin: {usuario.is_admin}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**CPF:** {usuario.cpf}")
                        st.write(f"**E-mail:** {usuario.email}")
                        st.write(f"**WhatsApp:** {usuario.whatsapp}")
                        st.write(f"**Data de cadastro:** {usuario.data_cadastro.strftime('%d/%m/%Y %H:%M')}")
                    
                    with col2:
                        st.write(f"**Doações cadastradas:** {len(usuario.doadores)}")
                        st.write(f"**Solicitações cadastradas:** {len(usuario.receptores)}")
                        st.write(f"**Pets cadastrados:** {len(usuario.pets)}")
                    
                    # Toggle para status de admin
                    if st.button(f"{'🔴 Remover Admin' if usuario.is_admin else '🟢 Tornar Admin'}", 
                                key=f"admin_toggle_{usuario.id}"):
                        usuario.is_admin = not usuario.is_admin
                        session.commit()
                        st.success(f"Status de admin alterado para {usuario.login}")
                        st.rerun()

    # Fechar sessão
    session.close()