import pandas as pd
import numpy as np
from dataclasses import dataclass
from libs.data_cleaning import *


@dataclass
class Futuros:
    """
    Classe que trata os dados relativos a ativos Futuros - Mini Dolar e Mini Indice.
    """

    def pegar_somente_futuros(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["Descrição Ticker"].str.contains("WDO|WIN")]
        df.loc[:, "Descrição Ticker"] = df["Descrição Ticker"] + " - " + df["Ticker"]
        df.loc[:, "Ticker"] = df["Descrição Ticker"].str[:6]
        df.loc[:, "Preço unitário"] = np.where(
            df["Movimentação"] == "Compra",
            df["Preço unitário"] * -1,
            df["Preço unitário"],
        )

        return df
