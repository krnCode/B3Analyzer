import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
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
types_of_income: list = [
    "Juros",
    "Amortização",
    "Dividendo",
    "Juros Sobre Capital Próprio",
    "Rendimento",
]


# FUNCTIONS
# -------------------------------------------------------------
# Convert dataframe to excel
def convert_to_excel(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    return output


def convert_to_excel_multisheets(dfs: list, sheet_names: list) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for df, sheet_name in zip(dfs, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)

    return output


# Create main df from uploaded files
def create_df(files) -> pd.DataFrame:
    dfs = []
    if files:
        for file in files:
            df = pd.read_excel(io=file)
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        return df


# Clean main DF
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
    df["Preço unitário"] = df["Preço unitário"].replace(to_replace={"-": 0})
    df["Valor da Operação"] = df["Valor da Operação"].replace(to_replace={"-": 0})
    df = df.sort_values(by="Data", ascending=True)
    df[["Ticker", "Descrição Ticker"]] = df["Produto"].str.split(
        pat=" ", n=1, expand=True
    )
    df["Descrição Ticker"] = df["Descrição Ticker"].replace(
        to_replace={"- ": ""}, regex=True
    )
    df = df.drop(columns=["Produto"])
    df = df[
        [
            "Entrada/Saída",
            "Data",
            "Movimentação",
            "Ticker",
            "Descrição Ticker",
            "Instituição",
            "Quantidade",
            "Preço unitário",
            "Valor da Operação",
        ]
    ]

    return df


# Create stocks statements dfs


# Create funds statements dfs
def create_df_fii(df: pd.DataFrame) -> pd.DataFrame:
    df_fii = df[
        df["Descrição Ticker"].str.contains(
            "FII|INVESTIMENTO IMOBILIARIO|INVESTIMENTO IMOBILIÁRIO|INV IMOB"
        )
    ]
    df_fii = df_fii[df_fii["Ticker"].str.contains("11")]
    df_fii = df_fii[df_fii["Movimentação"] != "Rendimento"]
    df_fii["Valor da Operação"] = np.where(
        df_fii["Movimentação"] == "Amortização",
        df_fii["Valor da Operação"] * -1,
        df_fii["Valor da Operação"],
    )
    df_fii["Valor da Operação"] = np.where(
        df_fii["Movimentação"] == "Resgate",
        df_fii["Valor da Operação"] * -1,
        df_fii["Valor da Operação"],
    )
    df_fii = df_fii.sort_values(by="Data", ascending=True)

    return df_fii


def get_fii_by_period(df_fii: pd.DataFrame) -> pd.DataFrame:
    df_fii["Mes"] = df_fii["Data"].dt.month
    df_fii["Ano"] = df_fii["Data"].dt.year
    df_fii = df_fii.groupby(["Ano", "Mes"])["Valor da Operação"].sum()
    df_fii = (
        df_fii.unstack(level=1).sort_values(by="Ano", ascending=False).fillna(value=0)
    )
    df_fii["Total"] = df_fii.sum(axis=1)
    df_fii["Média"] = df_fii.filter(regex="[^Total]").mean(axis=1)

    return df_fii


def get_fii_by_ticker(df_fii: pd.DataFrame) -> pd.DataFrame:
    df_fii["Mes"] = df_fii["Data"].dt.month
    df_fii["Ano"] = df_fii["Data"].dt.year
    df_fii = df_fii.groupby(["Ticker", "Ano"])["Valor da Operação"].sum()
    df_fii = (
        df_fii.unstack(level=1).sort_values(by="Ticker", ascending=True).fillna(value=0)
    )
    df_fii["Total"] = df_fii.sum(axis=1)
    df_fii["Média"] = df_fii.filter(regex="[^Total]").mean(axis=1)

    return df_fii


# Create income statements dfs
def get_income_by_period(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Movimentação"].isin(types_of_income)]
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year
    df = df.groupby(["Ano", "Mes"])["Valor da Operação"].sum()
    df = df.unstack(level=1).sort_values(by="Ano", ascending=False).fillna(value=0)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


def get_income_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Movimentação"].isin(types_of_income)]
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year
    df = df.groupby(["Ticker", "Ano"])["Valor da Operação"].sum()
    df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


def get_income_by_type(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Movimentação"].isin(types_of_income)]
    df = df.rename(columns={"Movimentação": "Tipo"})
    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year
    df = df.groupby(["Tipo", "Ano"])["Valor da Operação"].sum()
    df = df.unstack().sort_values(by="Tipo", ascending=True).fillna(value=0)
    df["Total"] = df.sum(axis=1)
    df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    return df


# MAIN APP
# -------------------------------------------------------------
# Sidebar - Files
with st.sidebar:
    files = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

    st.markdown("---")


# Main df
df: pd.DataFrame = create_df(files)


# Display the data in streamlit when the dataframe is created, else display nothing
if df is not None:
    df = clean_df(df)

    # Filters
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

    # INVESTMENT STATEMENTS
    # Expander to show consolidated investment statements and button to export to excel
    with st.expander("Visualizar Extrato Consolidado"):
        st.markdown("### Extrato Consolidado")
        st.dataframe(
            data=df_filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
            },
        )

        # Convert dataframe in excel format for download
        df_excel = convert_to_excel(df_filtered)
        st.download_button(
            data=df_excel,
            label="Exportar Excel",
            file_name="extrato_consolidado_b3",
            key="extrato_consolidado_b3",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # INFLOW/OUTFLOW STATEMENTS
    # Expander to show inflow/outflow entries
    with st.expander("Visualizar Entras/Saídas"):

        # Filter inflow and outflow entries
        df_in = df_filtered[df_filtered["Entrada/Saída"].values == "Credito"]
        df_out = df_filtered[df_filtered["Entrada/Saída"].values == "Debito"]

        col1, col2 = st.columns([1, 1])

        col1.subheader("Entradas")
        col1.dataframe(
            df_in,
            hide_index=True,
            column_config={
                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
            },
        )

        col2.subheader("Saídas")
        col2.dataframe(
            df_out,
            hide_index=True,
            column_config={
                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY")
            },
        )

        dfs = [df_in, df_out]
        sheet_names = ["b3consolidado_entradas", "b3consolidado_saidas"]
        df_excel = convert_to_excel_multisheets(dfs=dfs, sheet_names=sheet_names)
        st.download_button(
            data=df_excel,
            label="Exportar Excel",
            file_name="extrato_consolidado_entradas_saidas_b3",
            key="extrato_consolidado_entradas_saidas_b3",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # FUNDS DATA
    # Expander to show FII data
    with st.expander("Visualizar FII"):

        st.subheader("FII - Fundos de Investimento Imobiliário")

        tab1, tab2 = st.tabs(["FII por Período", "FII por Ticker"])

        df_fii = create_df_fii(df=df_filtered)

        with tab1:
            st.dataframe(
                data=get_fii_by_period(df_fii=df_fii), use_container_width=True
            )

            chart_data_type = get_fii_by_period(df_fii=df_fii).reset_index()
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

        with tab2:
            st.dataframe(
                data=get_fii_by_ticker(df_fii=df_fii), use_container_width=True
            )

            chart_data_type = get_fii_by_ticker(df_fii=df_fii).reset_index()
            chart = (
                alt.Chart(chart_data_type)
                .mark_bar(color="red")
                .encode(y="Total", x=alt.X("Ticker"), color="Total")
                .interactive()
            )
            st.altair_chart(
                altair_chart=chart,
                use_container_width=True,
                theme="streamlit",
            )

    # INCOME DATA
    # Expander to show income data
    with st.expander("Visualizar Rendimentos"):

        st.subheader("Rendimentos")

        tab1, tab2, tab3 = st.tabs(
            [
                "Rendimentos por Período",
                "Rendimentos por Ticker",
                "Rendimentos por Tipo",
            ]
        )

        with tab1:
            st.dataframe(
                data=get_income_by_period(df_filtered),
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

            chart_data_type = get_income_by_period(df_filtered).reset_index()
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

        with tab2:
            st.dataframe(
                data=get_income_by_ticker(df_filtered),
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

            chart_data_type = get_income_by_ticker(df_filtered).reset_index()
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

        with tab3:
            st.dataframe(
                data=get_income_by_type(df_filtered),
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

            chart_data_type = get_income_by_ticker(df_filtered).reset_index()
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

        with st.sidebar:

            st.markdown(
                "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
            )
