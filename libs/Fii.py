import pandas as pd
import streamlit as st
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

    Atributos:
        df (pd.dataframe): Pandas dataframe com as movimentações de extrato para serem tratadas;
    """

    # df: pd.DataFrame

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


# TESTES DA CLASSE
# -----------------------------
# if __name__ == "__main__":
#     st.set_page_config(page_title="Classe FII", layout="wide")

#     extratos = st.file_uploader(label="Teste Rendimentos", accept_multiple_files=True)

#     if extratos:

#         df = ler_arquivos(extratos=extratos)
#         st.write("EXTRATO PADRÃO")
#         st.dataframe(data=df)

#         df = tratar_dados(df=df)
#         st.write("DADOS TRATADOS")
#         st.dataframe(data=df)

#         fundos_imob = Fii(df)
#         fii = fundos_imob.pegar_somente_fii(df=df)
#         st.write("SOMENTE RENDIMENTOS")
#         st.dataframe(data=fii)
