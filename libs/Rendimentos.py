import pandas as pd
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
