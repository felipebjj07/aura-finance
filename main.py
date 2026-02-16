
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração de Estilo Aura
st.set_page_config(page_title="Aura Finance Pro", page_icon="💎", layout="wide")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('financas_aura.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transacoes 
             (data TEXT, categoria TEXT, descricao TEXT, valor REAL, tipo TEXT)''')
conn.commit()

# --- SIDEBAR: METAS ---
st.sidebar.title("🎯 Metas de My Lord")
meta_gastos = st.sidebar.number_input("Meta de Gastos Mensais (R$)", value=2000.0)

# --- INTERFACE PRINCIPAL ---
st.title("💎 Aura Finance: Gestão de Elite")
st.markdown("---")

# Layout em colunas para o formulário
with st.expander("📥 Registrar Movimentação", expanded=False):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        desc = st.text_input("Descrição")
        cat = st.selectbox("Categoria", ["Alimentação", "Lazer", "Contas", "Transporte", "Investimento", "Outros"])
    with c2:
        val = st.number_input("Valor (R$)", min_value=0.01)
        data_mov = st.date_input("Data", datetime.now())
    with c3:
        tp = st.radio("Tipo", ["Saída", "Entrada"])
        if st.button("Confirmar"):
            c.execute("INSERT INTO transacoes VALUES (?,?,?,?,?)", (data_mov, cat, desc, val, tp))
            conn.commit()
            st.success("Registrado!")

# --- PROCESSAMENTO DE DADOS ---
df = pd.read_sql_query("SELECT * FROM transacoes", conn)

if not df.empty:
    df['valor'] = df['valor'].astype(float)
    total_saidas = df[df['tipo'] == 'Saída']['valor'].sum()
    total_entradas = df[df['tipo'] == 'Entrada']['valor'].sum()
    saldo = total_entradas - total_saidas

    # Indicadores Visuais
    col_met1, col_met2, col_met3 = st.columns(3)
    col_met1.metric("Saldo Geral", f"R$ {saldo:,.2f}")
    col_met2.metric("Total Saídas", f"R$ {total_saidas:,.2f}", delta="- Gastos", delta_color="inverse")
    
    # Barra de Progresso da Meta
    progresso = min(total_saidas / meta_gastos, 1.0)
    st.write(f"**Uso da Meta Mensal: {progresso*100:.1f}%**")
    st.progress(progresso)
    
    if total_saidas > meta_gastos:
        st.warning("⚠️ Atenção, my lord: A meta de gastos foi ultrapassada!")

    # Gráficos
    st.markdown("### Análise de Gastos")
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        # Gráfico de Pizza por Categoria
        gastos_cat = df[df['tipo'] == 'Saída'].groupby('categoria')['valor'].sum()
        st.write("**Distribuição por Categoria**")
        st.pie_chart(gastos_cat)

    with col_gr2:
        # Histórico de Transações
        st.write("**Últimos Registros**")
        st.dataframe(df.sort_values(by='data', ascending=False).head(10), use_container_width=True)

else:
    st.info("O cofre está vazio. Comece registrando suas finanças, my lord.")
