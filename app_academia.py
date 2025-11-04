import streamlit as st
import sqlite3
import pandas as pd
import datetime

def get_db_connection():
    conn = sqlite3.connect('bancodedados/academia.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS alunos(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nasc TEXT NOT NULL,
                cpf TEXT NOT NULL
            );
        """
    )
    conn.commit()
    conn.close()

def get_alunos():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM alunos", conn)
    conn.close()
    return df

def add_aluno(nome, data_nasc, cpf):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO alunos(nome, data_nasc, cpf)
                VALUES (?, ?, ?);
            """,
            (nome, data_nasc, cpf)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir dados: {e}")
        return False

def update_aluno(id, nome, data_nasc, cpf):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                UPDATE alunos SET nome = ?, data_nasc = ?, cpf = ?
                WHERE id = ?
            """,
            (nome, data_nasc, cpf, id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar dados: {e}")
        return False

def delete_aluno(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
                DELETE FROM alunos WHERE id = ?
            """,
            (id,)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir dados: {e}")
        return False

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🏋️Sistema de Gestão da Academia Osias 🏋️</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; font-weight: 300; margin-top: 0px;'>A melhor da cidade😉</h3>", unsafe_allow_html=True)

create_table()

st.header("Cadastrar Novo Aluno")

with st.form("form_add_aluno", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Aluno", placeholder="Digite o nome completo")
    with col2:
        cpf = st.text_input("CPF", placeholder="000.000.000-00")
    
    data_nasc = st.date_input("Data de Nascimento")

    submitted = st.form_submit_button("Cadastrar Aluno")

    if submitted:
        if nome and data_nasc and cpf:
            data_nasc_str = data_nasc.strftime("%Y-%m-%d")
            
            if add_aluno(nome, data_nasc_str, cpf):
                st.success(f"Aluno **{nome}** cadastrado com sucesso!")
                st.balloons()
        else:
            st.warning("Por favor, preencha todos os campos.")


st.header("Alunos Cadastrados")

df_alunos = get_alunos()

if df_alunos.empty:
    st.info("Ainda não há alunos cadastrados.")
else:
    st.dataframe(df_alunos, use_container_width=True)
    
    st.subheader("Gerenciar Aluno")
    
    aluno_options = [f"{row['id']} - {row['nome']}" for index, row in df_alunos.iterrows()]
    selected_aluno_str = st.selectbox("Selecione um aluno para atualizar ou excluir", aluno_options)
    
    if selected_aluno_str:
        selected_id = int(selected_aluno_str.split(" - ")[0])
        
        aluno_data = df_alunos[df_alunos['id'] == selected_id].iloc[0]
        
        tab_update, tab_delete = st.tabs(["Atualizar Dados", "Excluir Aluno"])

        with tab_update:
            st.write(f"**Editando Aluno:** {aluno_data['nome']}")
            
            with st.form("form_update_aluno"):
                try:
                    default_date = pd.to_datetime(aluno_data['data_nasc']).date()
                except:
                    default_date = datetime.date(2000, 1, 1)

                new_nome = st.text_input("Nome", value=aluno_data['nome'])
                new_data_nasc = st.date_input("Data de Nascimento", value=default_date)
                new_cpf = st.text_input("CPF", value=aluno_data['cpf'])
                
                update_submitted = st.form_submit_button("Atualizar Aluno")
                
                if update_submitted:
                    data_nasc_str = new_data_nasc.strftime("%Y-%m-%d")
                    if update_aluno(selected_id, new_nome, data_nasc_str, new_cpf):
                        st.success(f"Dados do aluno **{new_nome}** atualizados!")
                        st.rerun()
                    else:
                        st.error("Falha ao atualizar dados.")

        with tab_delete:
            st.write(f"**Excluindo Aluno:** {aluno_data['nome']}")
            st.warning(f"Atenção: Esta ação é irreversível. Deseja excluir o(a) aluno(a) com ID {selected_id}?")
            
            if st.button("Confirmar Exclusão", type="primary"):
                if delete_aluno(selected_id):
                    st.success(f"Aluno **{aluno_data['nome']}** excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("Falha ao excluir aluno.")

st.divider()

