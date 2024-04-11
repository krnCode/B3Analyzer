import pandas as pd
from dataclasses import dataclass

# PANDAS CONFIG
# -----------------------------
pd.set_option("future.no_silent_downcasting", True)


@dataclass
class Bdr:
    """
    Classe que trata os dados relativos a BDR.
    """

    def pegar_somente_bdr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa os dados do extrato e retorna somente as movimentações de BDRs.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações dos extratos para tratamento inicial.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com os dados tratados e somente com as movimentações de BDR.
        """
        df = df[df["Ticker"].str.contains("35|34|33|32|31")]

        return df
