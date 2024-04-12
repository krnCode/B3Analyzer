import pandas as pd
from dataclasses import dataclass

# PANDAS CONFIG
# -----------------------------
pd.set_option("future.no_silent_downcasting", True)


@dataclass
class Acoes:
    """
    Classe que trata os dados relativos a Ações.
    """

    def pegar_somente_acoes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa os dados do extrato e retorna somente as movimentações de Açoes.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações dos extratos para tratamento inicial.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com os dados tratados e somente com as movimentações de Ações.
        """
        df = df[(df["Ticker"].str.contains("3|4")) & (df["Ticker"].str.len() == 5)]

        return df
