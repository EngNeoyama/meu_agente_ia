import streamlit as st
import os
from utils.load_pdf import extract_text_from_pdf
from utils.load_docx import extract_text_from_docx
from utils.load_excel import extract_text_from_excel

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Agente IA de Arquivos", layout="wide")

st.title("📁 Agente de IA para Leitura de Arquivos")

# Caminho para a pasta com os arquivos
data_dir = "data"
arquivos = os.listdir(data_dir)

# --- ESCOLHA DO ARQUIVO ---
arquivo_escolhido = st.selectbox("Escolha um arquivo para análise:", arquivos)

# --- EXTRAÇÃO DO TEXTO ---
caminho_arquivo = os.path.join(data_dir, arquivo_escolhido)
extensao = arquivo_escolhido.split('.')[-1].lower()

if st.button("🔍 Ler e exibir conteúdo"):
    texto = ""
    if extensao == "pdf":
        texto = extract_text_from_pdf(caminho_arquivo)
    elif extensao == "docx":
        texto = extract_text_from_docx(caminho_arquivo)
    elif extensao in ["xls", "xlsx"]:
        texto = extract_text_from_excel(caminho_arquivo)
    elif extensao == "txt":
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            texto = f.read()
    else:
        st.error("Formato não suportado.")
        texto = ""

    st.subheader("📄 Conteúdo extraído:")
    st.text_area("Texto:", texto, height=400)

    # Opcional: responder perguntas com IA usando OpenAI ou outro modelo
    if "openai" in st.secrets:
        import openai
        openai.api_key = st.secrets["openai"]["api_key"]

        pergunta = st.text_input("❓ Faça uma pergunta sobre o conteúdo:")
        if pergunta:
            with st.spinner("Processando..."):
                resposta = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um assistente que responde com base no conteúdo do arquivo."},
                        {"role": "user", "content": f"Arquivo:\n{texto[:4000]}"},
                        {"role": "user", "content": pergunta}
                    ]
                )
                st.success(resposta.choices[0].message.content)
