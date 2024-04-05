import pandas as pd
import streamlit as st
from dataclasses import dataclass

# PANDAS CONFIG
# -----------------------------
pd.set_option("future.no_silent_downcasting", True)


# CONSTANTES
# -----------------------------
# Descrição das movimentações a serem consideradas como rendimento
TIPOS_DE_RENDIMENTO: list = [
    "Amortização",
    "Dividendo",
    "Juros",
    "Juros Sobre Capital Próprio",
    "Rendimento",
]


@dataclass
class Rendimentos:
    """
    Classe que trata os dados relativos aos rendimentos com aplicações financeiras.

    São considerados rendimentos:
    Amortização, Dividendo, Juros, Juros Sobre Capital Próprio e Rendimento.
    """

    def pegar_somente_rendimentos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa os dados do extrato e retorna somente as movimentações de rendimento informadas em TIPOS_DE_RENDIMENTO (list).

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações dos extratos para tratamento inicial.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com os dados tratados e somente com as movimentações de rendimento informadas em TIPOS_DE_RENDIMENTO (list).
        """
        df = df[df["Movimentação"].isin(TIPOS_DE_RENDIMENTO)]

        return df

    def rendimentos_por_periodo(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos com as movimentações de rendimento e retona um dataframe com o total de rendimentos recebidos por mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por período.
        """
        df = df.groupby(["Ano", "Mes"], observed=True)["Valor da Operação"].sum()
        df = df.unstack(level=1).sort_values(by="Ano", ascending=False).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def rendimentos_por_ticker_mensal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos com as movimentações de rendimento e retona um dataframe com o total de rendimentos recebidos por ticker, mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por ticker, mes e ano.
        """
        df = df.groupby(["Ticker", "Ano", "Mes"])["Valor da Operação"].sum()
        df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def rendimentos_por_ticker_anual(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos com as movimentações de rendimento e retona um dataframe com o total de rendimentos recebidos por ticker e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por ticker e ano.
        """
        df = df.groupby(["Ticker", "Ano"])["Valor da Operação"].sum()
        df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def rendimentos_por_tipo_mensal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos com as movimentações de rendimento e retona um dataframe com o total de rendimentos recebidos por tipo, mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por tipo, mes e ano.
        """
        df = df.groupby(["Movimentação", "Ano", "Mes"])["Valor da Operação"].sum()
        df = df.unstack().sort_values(by="Movimentação", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def rendimentos_por_tipo_anual(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos com as movimentações de rendimento e retona um dataframe com o total de rendimentos recebidos por tipo e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por tipo e ano.
        """
        df = df.groupby(["Movimentação", "Ano"])["Valor da Operação"].sum()
        df = df.unstack().sort_values(by="Movimentação", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df


# TESTES DA CLASSE
# -----------------------------
# if __name__ == "__main__":
#     st.set_page_config(page_title="Classe Rendimentos", layout="wide")

#     extratos = st.file_uploader(label="Teste Rendimentos", accept_multiple_files=True)

#     if extratos:

#         df = ler_arquivos(extratos=extratos)
#         st.write("EXTRATO PADRÃO")
#         st.dataframe(data=df)

#         df = tratar_dados(df=df)
#         st.write("DADOS TRATADOS")
#         st.dataframe(data=df)

#         rendimentos = Rendimentos(df)
#         rend = rendimentos.pegar_somente_rendimentos(df=df)
#         st.write("SOMENTE RENDIMENTOS")
#         st.dataframe(data=rend)

#         rend_periodo = rendimentos.rendimentos_por_periodo(df=rend)
#         st.write("RENDIMENTOS POR PERÍODO")
#         st.dataframe(data=rend_periodo)

#         rend_ticker_mensal = rendimentos.rendimentos_por_ticker_mensal(df=rend)
#         st.write("RENDIMENTOS POR TICKER MENSAL")
#         st.dataframe(data=rend_ticker_mensal)

#         rend_ticker_anual = rendimentos.rendimentos_por_ticker_anual(df=rend)
#         st.write("RENDIMENTOS POR TICKER ANUAL")
#         st.dataframe(data=rend_ticker_anual)

#         rend_tipo_mensal = rendimentos.rendimentos_por_tipo_mensal(df=rend)
#         st.write("RENDIMENTOS POR TIPO MENSAL")
#         st.dataframe(data=rend_tipo_mensal)

#         rend_tipo_anual = rendimentos.rendimentos_por_tipo_anual(df=rend)
#         st.write("RENDIMENTOS POR TIPO ANUAL")
#         st.dataframe(data=rend_tipo_anual)
