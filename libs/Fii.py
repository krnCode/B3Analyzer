import pandas as pd
import numpy as np
from dataclasses import dataclass

# from libs.data_cleaning import *


# PANDAS CONFIG
# -----------------------------
pd.set_option("future.no_silent_downcasting", True)


@dataclass
class Fii:
    """
    Classe que trata os dados relativos aos FIIs - Fundos de Investimento imobiliário.
    """

    def pegar_somente_fii(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa os dados do extrato e retorna somente as movimentações de FIIs.

        Argumentos:
            df (pd.DataFrame): Pandas dataframe com as movimentações dos extratos para tratamento inicial.

        Retorna:
            df (pd.DataFrame): Pandas dataframe com os dados tratados e somente com as movimentações de FIIs.
        """
        df = df[
            df["Descrição Ticker"].str.contains(
                "FII|INVESTIMENTO IMOBILIARIO|INVESTIMENTO IMOBILIÁRIO|INV IMOB"
            )
        ]
        df = df[df["Ticker"].str.contains("11")]
        df = df[df["Movimentação"] != "Rendimento"]
        df["Valor da Operação"] = np.where(
            df["Movimentação"] == "Amortização",
            df["Valor da Operação"] * -1,
            df["Valor da Operação"],
        )
        df["Valor da Operação"] = np.where(
            df["Movimentação"] == "Resgate",
            df["Valor da Operação"] * -1,
            df["Valor da Operação"],
        )
        df = df.sort_values(by="Data", ascending=True)

        return df
