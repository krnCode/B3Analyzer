import pandas as pd
from dataclasses import dataclass


@dataclass
class PrecoMedio:
    """
    Classe que trata o cáculo do preço médio dos ativos.

    Para calcular corretamente, o ativo precisa ser agrupado para que o cálculo seja feito apenas no ativo
    """

    # TODO: Facilitar o cálculo do preço médio
    def calcular_preco_medio(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[
            df["Movimentação"].str.contains(
                "Transferência - Liquidação|Grupamento|Desdobro"
            )
        ]
        df["Saldo Quantidade"] = df["Quantidade"].where(
            df["Entrada/Saída"] == "Credito", -df["Quantidade"]
        )
        df["Saldo Valor"] = df["Valor da Operação"].where(
            df["Entrada/Saída"] == "Credito", -df["Valor da Operação"]
        )

        # Cálculo manual de soma cumulativa para considerar cenários de venda total, grupamento ou desdobramento
        # TODO: verificar outra forma de calcular agrupamento e desdobramentos
        # Mais prático atualizar todas as movimentações a partir da data de agrupamento/desdobro e utilizar função cumsum
        # apenas nas movimentações de entrada e saída
        saldo_valor = 0
        saldo_valores = []
        saldo_quantidade = 0
        saldo_quantidades = []
        for idx, row in df.iterrows():
            if row["Movimentação"] in ["Grupamento"]:
                saldo_quantidade = row["Quantidade"]
            else:
                saldo_quantidade += row["Saldo Quantidade"]
            saldo_valor += row["Saldo Valor"]
            if saldo_valor < 0:
                saldo_valor = 0
                saldo_quantidade = 0
            saldo_valores.append(saldo_valor)
            saldo_quantidades.append(saldo_quantidade)
        df["Saldo Valor"] = saldo_valores
        df["Saldo Quantidade"] = saldo_quantidades
        df["Preço Médio"] = df.apply(
            lambda row: (
                abs(row["Saldo Valor"] / row["Saldo Quantidade"])
                if row["Saldo Quantidade"] > 0
                else row["Valor da Operação"] / row["Quantidade"]
            ),
            axis=1,
        )

        return df
