import pandas as pd
import numpy as np
import streamlit as st


dfs = []


def create_dataframe(files, dfs):
    if files:
        st.markdown("### Extrato consolidado:")
        for file in files:
            df = pd.read_excel(io=file)
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        return df

    else:
        st.markdown("# Faça o upload dos seus extratos na tela lateral 👈")


with st.sidebar:
    files = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

df = create_dataframe(files, dfs)

if df is not None:
    # Clean "-" strings from numeric columns and display them as a single dataframe
    df["Preço unitário"] = df["Preço unitário"].replace("-", 0)
    df["Valor da Operação"] = df["Valor da Operação"].replace("-", 0)
    st.dataframe(data=df, use_container_width=True)

    # Convert the "data" column as a datetime type
    # Did not converted before displaying with "st.dataframe()"because the string format is easier to read
    df["Data"] = pd.to_datetime(df["Data"])
