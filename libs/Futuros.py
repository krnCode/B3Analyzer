import pandas as pd
import numpy as np
import streamlit as st
from dataclasses import dataclass
from libs.data_cleaning import *


@dataclass
class Futuros:
    """
    Classe que trata os dados relativos a ativos Futuros - Mini Dolar e Mini Indice.
    """

    def pegar_somente_futuros(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df["Descrição Ticker"].str.contains("WDO|WIN")]
        df["Descrição Ticker"] = df["Descrição Ticker"] + " - " + df["Ticker"]
        df["Ticker"] = df["Descrição Ticker"].str[:6]
        df["Preço unitário"] = np.where(
            df["Movimentação"] == "Compra",
            df["Preço unitário"] * -1,
            df["Preço unitário"],
        )

        return df

    def agrupar_daytrades(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.groupby(by=["Data"])["Preço unitário"].sum()

        return df
