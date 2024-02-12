import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

# APP PAGE CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="B3 Analyzer", layout="wide")


# CONSTANTS
# -------------------------------------------------------------
dfs = []


# FUNCTIONS
# -------------------------------------------------------------
def convert_to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return output


def create_dataframe(files, dfs):
    if files:
        st.markdown("### Extrato consolidado")
        for file in files:
            df = pd.read_excel(io=file)
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        return df

    else:
        st.markdown("# Faça o upload dos seus extratos na tela lateral 👈")


# MAIN APP
# -------------------------------------------------------------
with st.sidebar:
    files = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

if "files" not in st.session_state:
    st.session_state.files = files

df = create_dataframe(files, dfs)

# Created a session state for the dataframe so the user don't lose the uploaded files while browsing
if "df" not in st.session_state:
    st.session_state["df"] = df

# Display the data in streamlit when the dataframe is created, else display nothing
if df is not None:
    # Clean "-" strings from numeric columns and display them as a single dataframe
    df["Preço unitário"] = df["Preço unitário"].replace("-", 0)
    df["Valor da Operação"] = df["Valor da Operação"].replace("-", 0)

    # Changing outgoing entries to a negative number
    df["Valor da Operação"] = np.where(
        df["Entrada/Saída"] == "Debito",
        df["Valor da Operação"] * -1,
        df["Valor da Operação"],
    )

    df["Quantidade"] = np.where(
        df["Entrada/Saída"] == "Debito",
        df["Quantidade"] * -1,
        df["Quantidade"],
    )

    st.dataframe(data=df, use_container_width=True)

    # Convert dataframe in excel format for download
    df_excel = convert_to_excel(df)
    st.download_button(
        data=df_excel,
        label="Exportar Excel",
        file_name="extrato_consolidado_b3",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Filter "entradas" and "saídas"
    df_in = df[df["Entrada/Saída"].values == "Credito"]
    df_out = df[df["Entrada/Saída"].values == "Debito"]

    col1, col2 = st.columns([1, 1])

    col1.subheader("Entradas")
    col1.dataframe(df_in)

    col2.subheader("Saídas")
    col2.dataframe(df_out)

    # Convert the "data" column as a datetime datatype
    # Did not converted before displaying with "st.dataframe()" because the unformatted string is easier to read
    # df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
