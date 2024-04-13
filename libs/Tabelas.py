import pandas as pd
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

    # MARK: Tabelas Futuros
    # Com o objetivo de demonstrar os ganhos com daytrade em ativos futuros,
    # a lógica da tabela deste tipo de ativo é um pouco diferente e por isso
    # precisa de funções específicas para fazer o cálculo dos ganhos
    # em valor
    def futuros_por_dia(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadas por dia.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações agrupadas por dia.
        """
        df = df.groupby(["Data", "Ticker"])["Preço unitário"].sum()
        df = df.unstack(level=1).sort_values(by="Data", ascending=True).fillna(value=0)
        for ticker in df.columns:
            if "WDO" in ticker:
                df[f"{ticker}"] = df[ticker] * 10
            elif "WIN" in ticker:
                df[f"{ticker}"] = df[ticker] * 0.20
        df["Total"] = df.sum(axis=1)
        df["Média"] = df.filter(regex="[^Total]").mean(axis=1)

        return df

    def futuros_por_periodo(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe os dados limpos e retona um dataframe com as movimentações agrupadopor ticker, mes e ano.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações de rendimento já tratadas.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com as movimentações agrupadas por ticker, mes e ano.
        """
        df = df.groupby(
            ["Ticker", "Mes", "Ano"],
            observed=True,
        )["Preço unitário"].sum()
        df = (
            df.unstack(level=1).sort_values(by="Ticker", ascending=True).fillna(value=0)
        )
        for index in df.index:
            ticker = index[0]
            if "WDO" in ticker:
                df.loc[index] *= 10
            elif "WIN" in ticker:
                df.loc[index] *= 0.20
        df = df.assign(
            Total=df.sum(axis=1), Média=df.filter(regex="[^Total]").mean(axis=1)
        )

        return df
