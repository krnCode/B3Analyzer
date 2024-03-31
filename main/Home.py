import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import os
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image

# Inclusão do caminho do root do app para que o python consiga encontrar os packages em /libs
sys.path.insert(0, "./")

from libs.data_cleaning import *


# PANDAS CONFIG
# -------------------------------------------------------------
pd.set_option("display.precision", 2)
pd.get_option("display.precision")


# PAGINA DO APP CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="B3 Analyzer", layout="wide")


# CAMINHO PARA O LOGO
# -------------------------------------------------------------
caminho_app = Path(__file__).parent.parent
caminho_pasta_imagens = caminho_app / "res" / "logo"
listar_arquivos = os.listdir(caminho_pasta_imagens)
selecionar_imagem = listar_arquivos[0] if listar_arquivos else None
caminho_arquivo_imagem = caminho_pasta_imagens / selecionar_imagem


# APP PRINCIPAL
# -------------------------------------------------------------
# Sidebar - upload dos extratos
with st.sidebar:
    extratos = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

    st.markdown("---")


# Mostra as informações no Streamlit quando feito o upload dos extratos, senão mostra tela inicial informando apra fazer o upload.
if extratos:
    # Ler e concatenar extratos em um dataframe único
    df = ler_arquivos(extratos=extratos)

    # Tratar o dataframe gerado para análise
    df = tratar_dados(df=df)

    # Filtros
    with st.sidebar:
        st.markdown("Filtros:")

        statement = st.multiselect(
            label="Movimentação",
            options=df["Movimentação"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )
        ticker = st.multiselect(
            label="Ticker",
            options=df["Ticker"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )
        broker = st.multiselect(
            label="Corretora",
            options=df["Instituição"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )

        st.markdown("---")

        st.markdown(
            "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
        )

    # Lógica dos filtros
    query = []
    if statement:
        query.append(f"Movimentação == {statement}")

    if ticker:
        query.append(f"Ticker == {ticker}")

    if broker:
        query.append(f"Instituição == {broker}")

    if query:
        df_filtered = df.query(" and ".join(query))

    else:
        df_filtered = df

    st.dataframe(data=df_filtered)

else:
    # Mostrar mensagem de erro se o logo não for encontrado
    if not selecionar_imagem:
        st.write("Não foram encontradas imagens na pasta.")

    else:
        logo_path = caminho_pasta_imagens / selecionar_imagem
        img = Image.open(logo_path)
        st.image(img, width=250)

        st.markdown("# B3 Analyzer")

        st.markdown(
            """
            Bem vindo ao B3 Analyzer!

            Este app tem o objetivo de fornecer informações sobre os investimentos na bolsa de valores com base nos extratos fornecidos pela B3.

            Faça o upload dos extratos da B3 na tela lateral para que as análises sejam apresentadas.
            
            **Dica**: faça o download dos extratos por ano na B3, e faça o upload de todos os extratos para ver as informações consolidadas.

            """
        )

        st.markdown("---")

        st.markdown("### Faça o upload dos seus extratos na tela lateral 👈")

        with st.sidebar:

            st.markdown(
                "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
            )
