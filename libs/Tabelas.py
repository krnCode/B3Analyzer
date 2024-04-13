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
