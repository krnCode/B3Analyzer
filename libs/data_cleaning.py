import pandas as pd
from const import *


# Ler extratos e transformar em um dataframe único
def ler_arquivos(extratos) -> pd.DataFrame:
    """
    Lê todos os extratos enviados e transforma em um dataframe único.

    Argumentos:
        extratos: Extratos enviados para upload no formato em excel (.xlsx) para leitura.

    Retorna:
        df (pd.DataFrame): Pandas datraframe com todos os extratos em um único dataframe
    """
    dfs = []
    transformar_em_zero = lambda x: 0 if x == "-" else x

    for extrato in extratos:
        df = pd.read_excel(
            io=extrato,
            converters={
                "Preço unitário": transformar_em_zero,
                "Valor da Operação": transformar_em_zero,
            },
        )
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    return df


# Tratamento inicial dos dados para análise
def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa os dados do extrato e retorna um dataframe padronizado para análise.

    Argumentos:
        df (pd.DataFrame): Pandas dataframe com os extratos originais para tratamento.

    Retorna:
        df (pd.DataFrame): Pandas dataframe com os dados tratados para posterior análise.
    """
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y")
    df[["Ticker", "Descrição Ticker"]] = df["Produto"].str.split(
        pat=" ", n=1, expand=True
    )
    df["Descrição Ticker"] = df["Descrição Ticker"].replace(
        to_replace={"- ": ""}, regex=True
    )

    # Criar mask do df original para separar apenas onde a descrição do ticket contém
    # as iniciais de ativos futuros para nomear o ticker
    mask = df["Descrição Ticker"].str.contains("WDO|WIN")
    df.loc[mask, "Descrição Ticker"] = (
        df.loc[mask, "Descrição Ticker"] + " - " + df.loc[mask, "Ticker"]
    )
    df.loc[mask, "Ticker"] = df.loc[mask, "Descrição Ticker"].str[:6]

    df = df.assign(Mes=df["Data"].dt.month_name(locale="pt_BR"), Ano=df["Data"].dt.year)
    df["Mes"] = pd.Categorical(df["Mes"], categories=MESES, ordered=True)
    df = df[
        [
            "Entrada/Saída",
            "Ano",
            "Mes",
            "Data",
            "Ticker",
            "Descrição Ticker",
            "Movimentação",
            "Instituição",
            "Quantidade",
            "Preço unitário",
            "Valor da Operação",
        ]
    ]

    print(df["Mes"].unique())
    return df
