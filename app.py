import streamlit as st
import requests

def perguntar_para_huggingface(texto, pergunta):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {st.secrets['huggingface']['api_key']}"
    }
    prompt = f"""
    Aja como um assistente que responde com base no conteúdo de um documento.
    Documento: {texto[:3000]}
    Pergunta: {pergunta}
    Resposta:"""
    
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": 0.5, "max_new_tokens": 200}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    resposta = response.json()

    if isinstance(resposta, list) and "generated_text" in resposta[0]:
        return resposta[0]["generated_text"].split("Resposta:")[-1].strip()
    elif isinstance(resposta, dict) and "error" in resposta:
        return f"Erro: {resposta['error']}"
    else:
        return "Resposta não compreendida."
