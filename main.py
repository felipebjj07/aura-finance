import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Aura Finance", layout="centered")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('financas_aura.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS transacoes 
             (data TEXT, categoria TEXT, descricao TEXT, valor REAL, tipo TEXT)''')
conn.commit()

# --- INTERFACE ---
st.title("💰 Aura Finance: Gestão de Contas")
st.markdown("---")

# Formulário de Entrada
with st.expander("➕ Nova Transação"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.now())
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col2:
        tipo = st.selectbox("Tipo", ["Saída", "Entrada"])
        categoria = st.selectbox("Categoria", ["Alimentação", "Lazer", "Contas Fixas", "Investimento", "Salário", "Outros"])
    
    descricao = st.text_input("Descrição (Ex: Aluguel, Mercado...)")
    
    if st.button("Salvar Transação"):
        c.execute("INSERT INTO transacoes VALUES (?,?,?,?,?)", (data, categoria, descricao, valor, tipo))
        conn.commit()
        st.success("Registrado com sucesso!")

# --- DASHBOARD ---
df = pd.read_sql_query("SELECT * FROM transacoes", conn)

if not df.empty:
    # Cálculos
    entradas = df[df['tipo'] == 'Entrada']['valor'].sum()
    saidas = df[df['tipo'] == 'Saída']['valor'].sum()
    saldo = entradas - saidas

    # Cartões de Resumo
    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"R$ {entradas:,.2f}")
    c2.metric("Saídas", f"R$ {saidas:,.2f}", delta_color="inverse")
    c3.metric("Saldo Atual", f"R$ {saldo:,.2f}")

    # Gráfico
    st.subheader("Gastos por Categoria")
    fig_df = df[df['tipo'] == 'Saída'].groupby('categoria')['valor'].sum()
    st.bar_chart(fig_df)

    # Tabela
    st.subheader("Histórico Recente")
    st.dataframe(df.sort_values(by='data', ascending=False), use_container_width=True)
else:
    st.info("Aguardando os primeiros registros, my lord.")
