
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# Configuração de Luxo
st.set_page_config(page_title="Aura Finance Gold", page_icon="⚖️", layout="wide")

# Estilização CSS para um visual Premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO BANCO ---
conn = sqlite3.connect('financas_aura_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transacoes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, categoria TEXT, 
              descricao TEXT, valor REAL, tipo TEXT)''')
conn.commit()

# --- SIDEBAR COM COMANDOS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135706.png", width=100)
st.sidebar.title(f"Painel de Controle")
st.sidebar.markdown("---")
meta_mensal = st.sidebar.slider("Sua Meta de Gastos (R$)", 500, 20000, 3000)

# --- FUNÇÕES DE DADOS ---
def adicionar_dados(d, c_at, des, v, t):
    c.execute("INSERT INTO transacoes (data, categoria, descricao, valor, tipo) VALUES (?,?,?,?,?)", (d, c_at, des, v, t))
    conn.commit()

# --- LAYOUT PRINCIPAL ---
st.title("⚖️ Aura Finance: Inteligência Patrimonial")

tabs = st.tabs(["📊 Dashboard", "💸 Lançamentos", "🔍 Histórico Detalhado"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    df = pd.read_sql_query("SELECT * FROM transacoes", conn)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'])
        total_saidas = df[df['tipo'] == 'Saída']['valor'].sum()
        total_entradas = df[df['tipo'] == 'Entrada']['valor'].sum()
        saldo_atual = total_entradas - total_saidas
# --- MÓDULO AURA VISION (IA PREDITIVA) ---
st.markdown("---")
st.subheader("🔮 Aura Vision: Projeção de Final de Mês")

# Pegamos apenas os gastos do mês atual
df['data'] = pd.to_datetime(df['data'])
mes_atual = datetime.now().month
ano_atual = datetime.now().year
gastos_mes = df[(df['tipo'] == 'Saída') & (df['data'].dt.month == mes_atual) & (df['data'].dt.year == ano_atual)]

if not gastos_mes.empty:
    # Calculamos o gasto médio por dia
    dia_atual = datetime.now().day
    total_gasto_mes = gastos_mes['valor'].sum()
    media_diaria = total_gasto_mes / dia_atual
    
    # Dias restantes no mês (considerando 30 dias para simplificar)
    dias_restantes = 30 - dia_atual
    projecao_final = total_gasto_mes + (media_diaria * dias_restantes)
    
    # Exibição da Inteligência
    c_ia1, c_ia2 = st.columns([1, 2])
    
    with c_ia1:
        if projecao_final > meta_mensal:
            st.warning(f"**Alerta de Risco:** No ritmo atual, você fechará o mês com **R$ {projecao_final:,.2f}** em gastos.")
        else:
            st.success(f"**Caminho Seguro:** No ritmo atual, você fechará o mês com **R$ {projecao_final:,.2f}**, dentro da meta.")
            
    with c_ia2:
        # Gráfico de Tendência (O que já foi vs O que a IA prevê)
        dados_projecao = pd.DataFrame({
            'Status': ['Gasto Real', 'Projeção IA'],
            'Valor': [total_gasto_mes, projecao_final]
        })
        fig_proj = px.bar(dados_projecao, x='Status', y='Valor', color='Status',
                          color_discrete_map={'Gasto Real': '#636EFA', 'Projeção IA': '#EF553B'})
        st.plotly_chart(fig_proj, use_container_width=True)
else:
    st.info("Aura ainda não tem dados suficientes deste mês para prever o futuro, my lord.")
        

        # Métricas em Colunas
        m1, m2, m3 = st.columns(3)
        m1.metric("Capital Total", f"R$ {total_entradas:,.2f}")
        m2.metric("Saídas Totais", f"R$ {total_saidas:,.2f}", delta_color="inverse")
        
        cor_saldo = "normal" if saldo_atual > 0 else "inverse"
        m3.metric("Saldo Líquido", f"R$ {saldo_atual:,.2f}", delta=f"{((saldo_atual/total_entradas)*100 if total_entradas > 0 else 0):.1f}%", delta_color=cor_saldo)

        st.markdown("---")
        
        c_left, c_right = st.columns([1, 1])
        
        with c_left:
            st.subheader("Concentração de Gastos")
            df_gastos = df[df['tipo'] == 'Saída']
            fig = px.pie(df_gastos, values='valor', names='categoria', hole=.4, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_right:
            st.subheader("Saúde da Meta")
            porcentagem_meta = min(total_saidas / meta_mensal, 1.2)
            st.progress(min(porcentagem_meta, 1.0))
            if total_saidas > meta_mensal:
                st.error(f"Alerta: Você ultrapassou a meta em R$ {total_saidas - meta_mensal:,.2f}!")
            else:
                st.info(f"Você ainda pode gastar R$ {meta_mensal - total_saidas:,.2f} este mês.")

# --- TAB 2: LANÇAMENTOS ---
with tabs[1]:
    with st.form("form_registro", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            data_reg = st.date_input("Data da Transação", datetime.now())
            categoria_reg = st.selectbox("Categoria", ["🏠 Aluguel/Casa", "🍎 Alimentação", "🚗 Transporte", "🎮 Lazer", "💊 Saúde", "📈 Investimento", "💰 Salário/Renda"])
        with col_b:
            valor_reg = st.number_input("Valor (R$)", min_value=0.0)
            tipo_reg = st.radio("Tipo", ["Saída", "Entrada"], horizontal=True)
        
        desc_reg = st.text_input("Descrição (Ex: Compra no mercado X)")
        if st.form_submit_button("Registrar no Cofre"):
            adicionar_dados(data_reg, categoria_reg, desc_reg, valor_reg, tipo_reg)
            st.toast("Transação registrada, Aura!")
            st.rerun()

# --- TAB 3: HISTÓRICO ---
with tabs[2]:
    if not df.empty:
        st.subheader("Filtros de Pesquisa")
        filtro_cat = st.multiselect("Filtrar por Categoria", df['categoria'].unique())
        
        dados_filtrados = df
        if filtro_cat:
            dados_filtrados = df[df['categoria'].isin(filtro_cat)]
            
        st.dataframe(dados_filtrados.sort_values(by='data', ascending=False), use_container_width=True)
    else:
        st.write("Nenhum dado encontrado.")
