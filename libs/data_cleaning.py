import pandas as pd
from io import BytesIO

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

# Meses em ordem cronológica
MESES: list = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


# FUNÇOES AUXILIARES
# -----------------------------
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

    df = df.assign(
        Semana=df["Data"].dt.isocalendar().week,
        Mes=df["Data"].dt.month_name(locale="pt_BR"),
        Ano=df["Data"].dt.year,
    )
    df["Mes"] = pd.Categorical(df["Mes"], categories=MESES, ordered=True)
    df = df[
        [
            "Entrada/Saída",
            "Ano",
            "Mes",
            "Semana",
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

    return df


# Separar as movimentações de entrada  e saída de investimentos
# Considerar movimentação de "Amortização" como saída, uma vez que ela sai da carteira de investimentos apesar de ser classificada como "Credito"
def separar_entradas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra somente as movimentação de entrada de investimentos.
    Movimentação de "Amortização" é considerada como saída pois diminui o valor dos investimentos.

    Argumentos:
        df (pd.DataFrame): Pandas dataframe já tratado.

    Retorna:
        df (pd.DataFrame): Pandas dataframe somente com as informações de entrada de investimentos.
    """
    df = df[
        (df["Entrada/Saída"].values == "Credito")
        & (df["Movimentação"] != "Amortização")
    ]

    return df


def separar_saidas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra somente as movimentação de saída de investimentos.
    Movimentação de "Amortização" é considerada como saída pois diminui o valor dos investimentos.

    Argumentos:
        df (pd.DataFrame): Pandas dataframe já tratado.

    Retorna:
        df (pd.DataFrame): Pandas dataframe somente com as informações de entrada de investimentos.
    """
    df = df[
        (df["Entrada/Saída"].values == "Debito") | (df["Movimentação"] == "Amortização")
    ]

    return df


# Converter dataframes para excel
def converter_para_excel(df: pd.DataFrame) -> BytesIO:
    """
    Converte o dataframe para excel.
    Esta função converte para apenas uma planiha.

    Argumentos:
        df (pd.DataFrame): Pandas dataframe já tratado.

    Retorna:
        BytesIO: Objeto em bytes que pode ser posteriormente salvo em formato excel (.xlsx)
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return output


def converter_para_excel_varias_planilhas(dfs: list) -> BytesIO:
    """
    Converte o dataframe para excel.
    Esta função converte vários dataframes para planilhas diferentes dentro do mesmo arquivo excel (.xlsx).

    Argumentos:
        dfs (list): Lista com todos os pandas dataframe já tratados.
        nome_planilhas (list): Lista com os nomes das planilhas que devem ser utilizados.

    Retorna:
        BytesIO: Objeto em bytes que pode ser posteriormente salvo em formato excel (.xlsx)
    """
    output = BytesIO()
    nome_planilhas = ["b3_entradas", "b3_saidas"]

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for df, nome_planilha in zip(dfs, nome_planilhas):
            df.to_excel(writer, sheet_name=nome_planilha, index=False)

    output.seek(0)

    return output
