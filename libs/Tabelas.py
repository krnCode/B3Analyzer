import pandas as pd
import streamlit as st
from dataclasses import dataclass
from libs.data_cleaning import *


@dataclass
class Tabelas:
    """
    Classe que transforma os dados em tabelas de diferentes tipos.

    Os dados são primeiramente separados pelo tipo de ativo, e depois informados no tipo de tabela a ser apresentado.
    As tabelas são basicamente agrupamento de ativos por período, mes, ano, ticker, ou qualquer outro tipod de
    agrupoamento de dados que traga informação relevante para o usuário.
    """

    def por_periodo(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadas por período (mes e ano).

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações agrupadas por período.
        """
        df = df.groupby(["Ano", "Mes"], observed=True)["Valor da Operação"].sum()
        df = df.unstack(level=1).sort_values(by="Ano", ascending=False).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def ticker_mensal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadopor ticker, mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações agrupadas por ticker, mes e ano.
        """
        df = df.groupby(["Ticker", "Ano", "Mes"], observed=True)[
            "Valor da Operação"
        ].sum()
        df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def ticker_anual(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadas por ticker e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações por ticker e ano.
        """
        df = df.groupby(["Ticker", "Ano"], observed=True)["Valor da Operação"].sum()
        df = df.unstack().sort_values(by="Ticker", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def tipo_mensal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadas por tipo, mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento por tipo, mes e ano.
        """
        df = df.groupby(["Movimentação", "Ano", "Mes"], observed=True)[
            "Valor da Operação"
        ].sum()
        df = df.unstack().sort_values(by="Movimentação", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df

    def tipo_anual(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadas por tipo e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações agrupadas por tipo e ano.
        """
        df = df.groupby(["Movimentação", "Ano"], observed=True)[
            "Valor da Operação"
        ].sum()
        df = df.unstack().sort_values(by="Movimentação", ascending=True).fillna(value=0)
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df


# TESTES DA CLASSE
# -----------------------------
# if __name__ == "__main__":
#     st.set_page_config(page_title="Classe Tabelas", layout="wide")

#     extratos = st.file_uploader(label="Teste Tabelas", accept_multiple_files=True)

#     if extratos:

#         df = ler_arquivos(extratos=extratos)
#         st.write("EXTRATO PADRÃO")
#         st.dataframe(data=df)

#         df = tratar_dados(df=df)
#         st.write("DADOS TRATADOS")
#         st.dataframe(data=df)

#         col1, col2 = st.columns(spec=[1, 1])
#         tabelas = Tabelas(df=df)

#         with col1:
#             rendimentos = Rendimentos(df)
#             rend = rendimentos.pegar_somente_rendimentos(df=df)
#             st.write("SOMENTE RENDIMENTOS")
#             st.dataframe(data=rend)

#             rend_periodo = tabelas.por_periodo(df=rend)
#             st.write("RENDIMENTOS POR PERÍODO")
#             st.dataframe(data=rend_periodo)

#             rend_ticker_mensal = tabelas.ticker_mensal(df=rend)
#             st.write("RENDIMENTOS POR TICKER MENSAL")
#             st.dataframe(data=rend_ticker_mensal)

#             rend_ticker_anual = tabelas.ticker_anual(df=rend)
#             st.write("RENDIMENTOS POR TICKER ANUAL")
#             st.dataframe(data=rend_ticker_anual)

#             rend_tipo_mensal = tabelas.tipo_mensal(df=rend)
#             st.write("RENDIMENTOS POR TIPO MENSAL")
#             st.dataframe(data=rend_tipo_mensal)

#             rend_tipo_anual = tabelas.tipo_anual(df=rend)
#             st.write("RENDIMENTOS POR TIPO ANUAL")
#             st.dataframe(data=rend_tipo_anual)

#         with col2:
#             fundos = Fii()
#             fii = fundos.pegar_somente_fii(df=df)
#             st.write("SOMENTE FII")
#             st.dataframe(data=fii)

#             fii_periodo = tabelas.por_periodo(df=fii)
#             st.write("FII POR PERÍODO")
#             st.dataframe(data=fii_periodo)

#             fii_ticker_mensal = tabelas.ticker_mensal(df=fii)
#             st.write("FII POR TICKER MENSAL")
#             st.dataframe(data=fii_ticker_mensal)

#             fii_ticker_anual = tabelas.ticker_anual(df=fii)
#             st.write("FII POR TICKER ANUAL")
#             st.dataframe(data=fii_ticker_anual)

#             fii_tipo_mensal = tabelas.tipo_mensal(df=fii)
#             st.write("FII POR TIPO MENSAL")
#             st.dataframe(data=fii_tipo_mensal)

#             fii_tipo_anual = tabelas.tipo_anual(df=fii)
#             st.write("FII POR TIPO ANUAL")
#             st.dataframe(data=fii_tipo_anual)
