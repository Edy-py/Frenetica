# -*- coding: utf-8 -*-
import unicodedata
import streamlit as st
import os
import base64
import re

def format_currency(value):
    """Converte um float para string no formato R$ 1.234,56"""
    try:
        if value is None:
            return "R$ 0,00"
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def parse_currency(curr_str):
    """Converte uma string formatada (R$ 1.234,56) para float (1234.56)"""
    if not curr_str or not isinstance(curr_str, str):
        return 0.0
    try:
        clean_str = curr_str.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        return float(clean_str)
    except (ValueError, TypeError):
        return 0.0
    
def format_telefone(telefone):
    """Formata um número de telefone para o padrão (XX) XXXXX-XXXX"""
    if not telefone or not isinstance(telefone, str):
        return ""
    digits = ''.join(filter(str.isdigit, telefone))
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    else:
        return telefone 

def clean_text(text):
    """Remove acentos, espaços extras e converte para maiúsculas (Padronização para o Banco)"""
    if not text or not isinstance(text, str):
        return ""
    try:
        nfkd_form = unicodedata.normalize('NFKD', text)
        text_normalized = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        return text_normalized.upper().strip()
    except Exception:
        return text.upper().strip()

def salvar_imagem(upload_file, subpasta):
    """Salva o arquivo na pasta imagens/{subpasta} e retorna o nome do arquivo."""
    if upload_file is not None:
        diretorio = os.path.join("imagens", subpasta)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
        
        caminho_completo = os.path.join(diretorio, upload_file.name)
        
        with open(caminho_completo, "wb") as f:
            f.write(upload_file.getbuffer())
        
        return upload_file.name 
    return None

def get_base64_image(image_path):
    """Converte imagem local para Base64 para exibição em HTML (Cards)"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except Exception:
        return None

def get_role_color(role):
    """Helper visual para indicar o nível de acesso no sistema"""
    colors = {
        "admin": "blue",
        "financeiro": "green",
        "vendedor": "orange",
        "parceiro": "purple",
        "cliente": "gray"
    }
    return colors.get(role, "gray")

def validar_telefone(telefone):
    """
    Verifica se o telefone tem 11 dígitos (DDD + 9 + número)
    Exemplo aceito: 64912345678
    """
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', telefone)
    
    # Verifica se tem 11 dígitos e se começa com DDD válido (2 dígitos) + o 9
    # Regex: ^[1-9]{2} (DDD) + 9 (prefixo celular) + [0-9]{8} (restante)
    padrao = r'^[1-9]{2}9[0-9]{8}$'
    
    if re.match(padrao, apenas_numeros):
        return True, apenas_numeros
    return False, apenas_numeros

def validar_cpf(cpf):
    """
    Valida e limpa o CPF. Retorna (True, cpf_limpo) ou (False, cpf_limpo).
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', str(cpf))

    # Verifica se tem 11 dígitos ou se é uma sequência repetida (ex: 111.111.111-11)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False, cpf

    # Cálculo dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False, cpf

    return True, cpf