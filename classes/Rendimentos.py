import pandas as pd
import streamlit as st
from dataclasses import dataclass

pd.set_option("future.no_silent_downcasting", True)

TIPOS_DE_RENDIMENTO: list = [
    "Juros",
    "Amortização",
    "Dividendo",
    "Juros Sobre Capital Próprio",
    "Rendimento",
]


@dataclass
class Rendimentos:
    df: pd.DataFrame

    def pegar_somente_rendimentos(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
        df = df[df["Movimentação"].isin(TIPOS_DE_RENDIMENTO)]

        return df

    def rendimentos_por_periodo(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(Mes=df["Data"].dt.month, Ano=df["Data"].dt.year)
        df = df.groupby(["Ano", "Mes"])["Valor da Operação"].sum()
        df = df.unstack(level=1).sort_values(by="Ano", ascending=False).fillna(value=0)
        df["Total"] = df.sum(axis=1)
        df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

        return df

    # def get_income_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    #     df = df[df["Movimentação"].isin(TIPOS_DE_RENDIMENTO)]
    #     df.loc[:, "Mes"] = df["Data"].dt.month
    #     df.loc[:, "Ano"] = df["Data"].dt.year
    #     df = df.groupby(["Ticker", "Ano"])["Valor da Operação"].sum()
    #     df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
    #     df["Total"] = df.sum(axis=1)
    #     df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    #     return df

    # def get_income_by_type(df: pd.DataFrame) -> pd.DataFrame:
    #     df = df[df["Movimentação"].isin(TIPOS_DE_RENDIMENTO)]
    #     df = df.rename(columns={"Movimentação": "Tipo"})
    #     df.loc[:, "Mes"] = df["Data"].dt.month
    #     df.loc[:, "Ano"] = df["Data"].dt.year
    #     df = df.groupby(["Tipo", "Ano"])["Valor da Operação"].sum()
    #     df = df.unstack().sort_values(by="Tipo", ascending=True).fillna(value=0)
    #     df["Total"] = df.sum(axis=1)
    #     df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

    #     return df


if __name__ == "__main__":
    extratos = st.file_uploader(label="Teste Rendimentos", accept_multiple_files=True)

    def ler_arquivos(extratos) -> pd.DataFrame:
        dfs = []
        for extrato in extratos:
            df = pd.read_excel(io=extrato)
            dfs.append(df)
        df = pd.concat(dfs, ignore_index=True)
        return df

    if extratos:

        df = ler_arquivos(extratos=extratos)

        rendimentos = Rendimentos(df)
        st.dataframe(data=df)

        rend = rendimentos.pegar_somente_rendimentos(df=df)
        st.dataframe(data=rend)

        rend_periodo = rendimentos.rendimentos_por_periodo(df=rend)
        st.dataframe(data=rend_periodo)
