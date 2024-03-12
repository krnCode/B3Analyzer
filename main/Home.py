import pandas as pd
import streamlit as st
import altair as alt
import os
from io import BytesIO
from pathlib import Path
from PIL import Image


# PANDAS CONFIG
# -------------------------------------------------------------
pd.set_option("display.precision", 2)
pd.get_option("display.precision")


# APP PAGE CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="B3 Analyzer", layout="wide")


# PATH TO LOGO
# -------------------------------------------------------------
current_path = Path(__file__).parent.parent
img_path = current_path / "res" / "logo"
img_files = os.listdir(img_path)
img_file = img_files[0] if img_files else None
img_file_path = img_path / img_file

# Statements to consider as income
types_of_income = [
    "Juros",
    "Amortização",
    "Dividendo",
    "Juros Sobre Capital Próprio",
    "Rendimento",
]


# FUNCTIONS
# -------------------------------------------------------------
def convert_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return output


def create_df(files):
    dfs = []
    if files:
        for file in files:
            df = pd.read_excel(io=file)
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        return df


def clean_df(df):
    # Convert column to datetime
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")

    # Clean "-" strings from numeric columns and display them as a single dataframe
    df["Preço unitário"] = df["Preço unitário"].replace(to_replace={"-": 0})
    df["Valor da Operação"] = df["Valor da Operação"].replace(to_replace={"-": 0})

    # Sort dataframe by date
    df = df.sort_values(by="Data", ascending=True)

    # Create custom columns
    df[["Ticker", "Descrição Ticker"]] = df["Produto"].str.split(
        pat=" ", n=1, expand=True
    )
    df["Descrição Ticker"] = df["Descrição Ticker"].replace(
        to_replace={"- ": ""}, regex=True
    )

    # Drop unused columns
    df = df.drop(columns=["Produto"])

    return df


def get_income_by_period(df):
    df = df[df["Movimentação"].isin(types_of_income)]
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    df = df.groupby(["Ano", "Mes"])["Valor da Operação"].sum()
    df = df.unstack(level=1).sort_values(by="Ano", ascending=False)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


def get_income_by_ticker(df):
    df = df[df["Movimentação"].isin(types_of_income)]
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    df = df.groupby(["Ticker", "Ano"])["Valor da Operação"].sum()
    df = df.unstack().sort_values(by="Ticker", ascending=True)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


def get_income_by_type(df):
    df = df[df["Movimentação"].isin(types_of_income)]
    df = df.rename(columns={"Movimentação": "Tipo"})
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    df = df.groupby(["Tipo", "Ano"])["Valor da Operação"].sum()
    df = df.unstack().sort_values(by="Tipo", ascending=True)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


# MAIN APP
# -------------------------------------------------------------

# Sidebar
with st.sidebar:
    files = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

    st.markdown("---")

    st.markdown(
        "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
    )

df = create_df(files)

# Display the data in streamlit when the dataframe is created, else display nothing
if df is not None:
    df = clean_df(df)

    # Expander to show consolidated investment statements and button to export to excel
    with st.expander("Visualizar Extrato Consolidado"):
        st.markdown("### Extrato Consolidado")
        st.dataframe(data=df, use_container_width=True, hide_index=True)

        # Convert dataframe in excel format for download
        df_excel = convert_to_excel(df)
        st.download_button(
            data=df_excel,
            label="Exportar Excel",
            file_name="extrato_consolidado_b3",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # Filter inflow and outflow entries
    df_in = df[df["Entrada/Saída"].values == "Credito"]
    df_out = df[df["Entrada/Saída"].values == "Debito"]

    # Expander to show inflow/outflow entries
    with st.expander("Visualizar Entras/Saídas"):

        col1, col2 = st.columns([1, 1])

        col1.subheader("Entradas")
        col1.dataframe(df_in, hide_index=True)

        col2.subheader("Saídas")
        col2.dataframe(df_out, hide_index=True)

    # INCOME DATA

    # Expander to show income data
    with st.expander("Visualizar Rendimentos"):

        st.subheader("Rendimentos")

        tab_table1, tab_table2, tab_table3 = st.tabs(
            [
                "Tabela - Rendimentos por Período",
                "Tabela - Rendimentos por Ticker",
                "Tabela - Rendimentos por Tipo",
            ]
        )

        with tab_table1:
            st.dataframe(
                data=get_income_by_period(df),
                use_container_width=True,
                column_config={
                    "Total": st.column_config.NumberColumn(
                        help="Valor total de rendimentos, por ano",
                        min_value=0,
                        step=0.01,
                    ),
                    "Média": st.column_config.NumberColumn(
                        help="Média de rendimentos, por ano",
                        min_value=0,
                        step=0.01,
                    ),
                },
            )

            chart_data_type = get_income_by_period(df).reset_index()
            chart = (
                alt.Chart(chart_data_type)
                .mark_bar(color="red")
                .encode(y="Total", x=alt.X("Ano:N"), color="Total")
                .interactive()
            )
            st.altair_chart(
                altair_chart=chart,
                use_container_width=True,
                theme="streamlit",
            )

        with tab_table2:
            st.dataframe(
                data=get_income_by_ticker(df),
                use_container_width=True,
                column_config={
                    "Total": st.column_config.NumberColumn(
                        help="Valor total de rendimentos",
                        min_value=0,
                        step=0.01,
                    ),
                    "Média": st.column_config.NumberColumn(
                        help="Média de rendimentos",
                        min_value=0,
                        step=0.01,
                    ),
                },
            )

            chart_data_type = get_income_by_ticker(df).reset_index()
            chart = (
                alt.Chart(chart_data_type)
                .mark_bar()
                .encode(y="Total", x="Ticker", color="Total")
                .interactive()
            )
            st.altair_chart(
                altair_chart=chart,
                use_container_width=True,
                theme="streamlit",
            )

        with tab_table3:
            st.dataframe(
                data=get_income_by_type(df),
                use_container_width=True,
                column_config={
                    "Total": st.column_config.NumberColumn(
                        help="Valor total de rendimentos",
                        min_value=0,
                        step=0.01,
                    ),
                    "Média": st.column_config.NumberColumn(
                        help="Média de rendimentos",
                        min_value=0,
                        step=0.01,
                    ),
                },
            )

            chart_data_type = get_income_by_ticker(df).reset_index()
            chart = (
                alt.Chart(chart_data_type)
                .mark_bar()
                .encode(y="Total", x="Ticker", color="Total")
                .interactive()
            )
            st.altair_chart(
                altair_chart=chart,
                use_container_width=True,
                theme="streamlit",
            )

        st.markdown("---")


else:
    # Show error message if logo is not found
    if not img_file:
        st.write("No images found in directory.")

    else:
        logo_path = img_path / img_file
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
