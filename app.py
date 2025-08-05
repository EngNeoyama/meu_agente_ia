import streamlit as st
import os
import requests

from utils.load_pdf import extract_text_from_pdf
from utils.load_docx import extract_text_from_docx
from utils.load_excel import extract_text_from_excel

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(page_title="Agente IA com Hugging Face", layout="wide")
st.title("🤖 Agente de IA para Análise de Arquivos")
st.markdown("Escolha um arquivo e pergunte qualquer coisa sobre o conteúdo!")

# ---------------- LISTA DE ARQUIVOS ----------------
data_dir = "data"
arquivos = [arq for arq in os.listdir(data_dir) if not arq.startswith('.')]

arquivo_escolhido = st.selectbox("📂 Escolha um arquivo:", arquivos)

# ---------------- LEITURA DO ARQUIVO ----------------
@st.cache_data(show_spinner=False)
def ler_arquivo(path):
    ext = path.split('.')[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(path)
    elif ext == "docx":
        return extract_text_from_docx(path)
    elif ext in ["xls", "xlsx"]:
        return extract_text_from_excel(path)
    elif ext == "txt":
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return None

# ---------------- FUNÇÃO PARA CONSULTAR HUGGING FACE ----------------
def perguntar_para_huggingface(texto, pergunta):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {st.secrets['huggingface']['api_key']}"
    }
    prompt = f"""Você é um assistente que responde com base no conteúdo de um documento.
Documento:
\"\"\"
{texto[:3000]}
\"\"\"

Pergunta: {pergunta}
Resposta:"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.3,
            "max_new_tokens": 200
        }
    }

    resposta = requests.post(API_URL, headers=headers, json=payload)

    try:
        resultado = resposta.json()
        if isinstance(resultado, list) and "generated_text" in resultado[0]:
            return resultado[0]["generated_text"].split("Resposta:")[-1].strip()
        elif "error" in resultado:
            return f"❌ Erro da API: {resultado['error']}"
        else:
            return "❌ Resposta não compreendida."
    except Exception as e:
        return f"❌ Erro inesperado: {e}"

# ---------------- EXECUÇÃO ----------------
if arquivo_escolhido:
    caminho = os.path.join(data_dir, arquivo_escolhido)
    texto = ler_arquivo(caminho)

    if texto:
        with st.expander("📄 Ver conteúdo extraído (opcional)"):
            st.text_area("Conteúdo do arquivo:", texto, height=300)

        pergunta = st.text_input("❓ Faça sua pergunta sobre o conteúdo do arquivo:")

        if pergunta.strip():
            with st.spinner("Consultando a IA..."):
                resposta = perguntar_para_huggingface(texto, pergunta)
                st.success("🧠 Resposta:")
                st.write(resposta)
    else:
        st.error("❌ Não foi possível ler o arquivo selecionado.")
