import pandas as pd
import streamlit as st
import os
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image
from libs.data_cleaning import *
from libs.Rendimentos import Rendimentos
from libs.Fii import Fii
from libs.Tabelas import Tabelas
from libs.Futuros import Futuros
from libs.Bdr import Bdr


# PANDAS CONFIG
# -------------------------------------------------------------
pd.set_option("display.precision", 2)
pd.get_option("display.precision")


# PAGINA DO APP CONFIG
# -------------------------------------------------------------
st.set_page_config(page_title="B3 Analyzer", layout="wide")


# CAMINHO PARA O LOGO
# -------------------------------------------------------------
caminho_app = Path(__file__).parent
caminho_pasta_imagens = caminho_app / "res" / "logo"
listar_arquivos = os.listdir(caminho_pasta_imagens)
selecionar_imagem = listar_arquivos[0] if listar_arquivos else None
caminho_arquivo_imagem = caminho_pasta_imagens / selecionar_imagem


# APP PRINCIPAL
# -------------------------------------------------------------
# MARK: Sidebar - upload dos extratos
with st.sidebar:
    extratos = st.file_uploader(
        label="Envie os extratos da B3 em excel (extensão .xlsx)",
        accept_multiple_files=True,
    )

    st.markdown("---")


# Mostra as informações no Streamlit quando feito o upload dos extratos, senão mostra tela inicial informando para fazer o upload.
if extratos:
    # Ler e concatenar extratos em um dataframe único
    df = ler_arquivos(extratos=extratos)

    # Tratar o dataframe gerado para análise
    df = tratar_dados(df=df)

    # MARK: Filtros
    with st.sidebar:
        st.markdown("Filtros:")

        col1, col2 = st.columns(spec=[1, 1])

        with col1:
            ano = st.multiselect(
                label="Ano",
                options=df["Ano"].sort_values(ascending=True).unique(),
                default=None,
                placeholder="",
            )

        with col2:
            mes = st.multiselect(
                label="Mes",
                options=df["Mes"].sort_values(ascending=True).unique(),
                default=None,
                placeholder="",
            )

        movimentação = st.multiselect(
            label="Movimentação",
            options=df["Movimentação"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )

        ticker = st.multiselect(
            label="Ticker",
            options=df["Ticker"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )

        corretora = st.multiselect(
            label="Corretora",
            options=df["Instituição"].sort_values(ascending=True).unique(),
            default=None,
            placeholder="",
        )

        st.markdown("---")

        st.markdown(
            "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
        )

    # MARK: Lógica dos filtros
    query = []
    if ano:
        query.append(f"Ano == {ano}")

    if mes:
        query.append(f"Mes == {mes}")

    if movimentação:
        query.append(f"Movimentação == {movimentação}")

    if ticker:
        query.append(f"Ticker == {ticker}")

    if corretora:
        query.append(f"Instituição == {corretora}")

    if query:
        df_filtered = df.query(" and ".join(query))

    else:
        df_filtered = df

    st.markdown("# Análise dos Investimentos")

    metricas, extratos, ativos = st.tabs(["Métricas", "Extratos", "Ativos"])
    tabelas = Tabelas()

    # MARK: Métricas
    # TODO: incluir métricas
    with metricas:
        pass

    # MARK: Extratos
    with extratos:
        st.markdown("#### Extrato Consolidado")
        st.dataframe(data=df_filtered, use_container_width=True)
        st.download_button(
            label="Exportar Excel",
            data=converter_para_excel(df_filtered),
            file_name="b3_extrato_consolidado.xlsx",
            key="b3_extrato_consolidado",
        )
        st.markdown("---")

        st.markdown("#### Entradas/Saídas")
        entradas = separar_entradas(df=df_filtered)
        saidas = separar_saidas(df=df_filtered)

        col1, col2 = st.columns(spec=[1, 1])

        with col1:
            st.markdown("##### Entradas")
            st.dataframe(data=entradas, use_container_width=True)

        with col2:
            st.markdown("##### Saídas")
            st.dataframe(data=saidas, use_container_width=True)

        st.download_button(
            label="Exportar Excel",
            data=converter_para_excel_varias_planilhas(
                dfs=[entradas, saidas], nome_planilhas=["Entradas", "Saídas"]
            ),
            file_name="b3_extrato_entradas_saidas.xlsx",
            key="b3_extrato_entradas_saidas",
        )
        st.markdown("---")

    # MARK: Ativos
    # TODO: incluir análises
    with ativos:
        selecao_ativo = st.radio(
            label="Selecione qual classe de ativo deseja ver:",
            options=["Ações", "FII", "BDR", "Futuros", "Rendimentos"],
            horizontal=True,
        )
        # MARK: Rendimentos
        if selecao_ativo == "Rendimentos":
            rendimentos = Rendimentos()
            rend = rendimentos.pegar_somente_rendimentos(df=df_filtered)

            st.download_button(
                label="Exportar Todas as Tabelas para Excel",
                data=converter_para_excel_varias_planilhas(
                    dfs=[
                        rend,
                        tabelas.por_periodo(df=rend).reset_index(),
                        tabelas.ticker_mensal(df=rend).reset_index(),
                        tabelas.ticker_anual(df=rend).reset_index(),
                        tabelas.tipo_mensal(df=rend).reset_index(),
                        tabelas.tipo_anual(df=rend).reset_index(),
                    ],
                    nome_planilhas=[
                        "Rend. Extrato Consolidado",
                        "Rend. Por Período",
                        "Rend. Ticker Mensal",
                        "Rend. Tiker Anual",
                        "Rend. Tipo Mensal",
                        "Rend. Tipo Anual",
                    ],
                ),
                file_name="b3_rendimentos.xlsx",
                key="b3_rendimentos",
            )

            st.markdown("#### Extrato Rendimentos")
            st.dataframe(data=rend, use_container_width=True)
            st.markdown("---")

            st.markdown("#### Rendimentos por Período")
            st.dataframe(
                data=tabelas.por_periodo(df=rend),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Rendimentos por Ticker - Mensal")
            st.dataframe(
                data=tabelas.ticker_mensal(df=rend),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Rendimentos por Ticker - Anual")
            st.dataframe(
                data=tabelas.ticker_anual(df=rend),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Rendimentos por Tipo - Mensal")
            st.dataframe(
                data=tabelas.tipo_mensal(df=rend),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Rendimentos por Tipo - Anual")
            st.dataframe(
                data=tabelas.tipo_anual(df=rend),
                use_container_width=True,
            )
            st.markdown("---")

        # MARK: FII
        if selecao_ativo == "FII":
            fundos = Fii()
            fii = fundos.pegar_somente_fii(df=df_filtered)

            st.download_button(
                label="Exportar Todas as Tabelas para Excel",
                data=converter_para_excel_varias_planilhas(
                    dfs=[
                        fii,
                        tabelas.por_periodo(df=fii).reset_index(),
                        tabelas.ticker_mensal(df=fii).reset_index(),
                        tabelas.ticker_anual(df=fii).reset_index(),
                        tabelas.tipo_mensal(df=fii).reset_index(),
                        tabelas.tipo_anual(df=fii).reset_index(),
                    ],
                    nome_planilhas=[
                        "FII Extrato Consolidado",
                        "FII Por Período",
                        "FII Ticker Mensal",
                        "FII Tiker Anual",
                        "FII Tipo Mensal",
                        "FII Tipo Anual",
                    ],
                ),
                file_name="b3_fii.xlsx",
                key="b3_fii",
            )

            st.markdown("#### Extrato FII")
            st.dataframe(data=fii, use_container_width=True)
            st.markdown("---")

            st.markdown("#### FII por Período")
            st.dataframe(
                data=tabelas.por_periodo(df=fii),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### FII por Ticker - Mensal")
            st.dataframe(
                data=tabelas.ticker_mensal(df=fii),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### FII por Ticker - Anual")
            st.dataframe(
                data=tabelas.ticker_anual(df=fii),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### FII por Tipo - Mensal")
            st.dataframe(
                data=tabelas.tipo_mensal(df=fii),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### FII por Tipo - Anual")
            st.dataframe(
                data=tabelas.tipo_anual(df=fii),
                use_container_width=True,
            )
            st.markdown("---")

        # MARK: BDR
        if selecao_ativo == "BDR":
            bdr = Bdr()
            bdr_mov = bdr.pegar_somente_bdr(df_filtered)

            st.download_button(
                label="Exportar Todas as Tabelas para Excel",
                data=converter_para_excel_varias_planilhas(
                    dfs=[
                        bdr_mov,
                        tabelas.por_periodo(df=bdr_mov).reset_index(),
                        tabelas.ticker_mensal(df=bdr_mov).reset_index(),
                        tabelas.ticker_anual(df=bdr_mov).reset_index(),
                        tabelas.tipo_mensal(df=bdr_mov).reset_index(),
                        tabelas.tipo_anual(df=bdr_mov).reset_index(),
                    ],
                    nome_planilhas=[
                        "BDR Extrato Consolidado",
                        "BDR Por Período",
                        "BDR Ticker Mensal",
                        "BDR Tiker Anual",
                        "BDR Tipo Mensal",
                        "BDR Tipo Anual",
                    ],
                ),
                file_name="b3_bdr.xlsx",
                key="b3_bdr",
            )

            st.markdown("#### Extrato BDRs")
            st.dataframe(data=bdr_mov, use_container_width=True)
            st.markdown("---")

            st.markdown("#### BDR por Período")
            st.dataframe(
                data=tabelas.por_periodo(df=bdr_mov),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### BDR por Ticker - Mensal")
            st.dataframe(
                data=tabelas.ticker_mensal(df=bdr_mov),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### BDR por Ticker - Anual")
            st.dataframe(
                data=tabelas.ticker_anual(df=bdr_mov),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### BDR por Tipo - Mensal")
            st.dataframe(
                data=tabelas.tipo_mensal(df=bdr_mov),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### BDR por Tipo - Anual")
            st.dataframe(
                data=tabelas.tipo_anual(df=bdr_mov),
                use_container_width=True,
            )
            st.markdown("---")

        # MARK: Futuros
        # TODO: Calcular pontos (coluna quantidade) e valor ganho (coluna valor da operação)
        if selecao_ativo == "Futuros":
            futuros = Futuros()
            fut = futuros.pegar_somente_futuros(df_filtered)
            futgroup = futuros.agrupar_daytrades(fut)

            st.download_button(
                label="Exportar Todas as Tabelas para Excel",
                data=converter_para_excel_varias_planilhas(
                    dfs=[
                        futgroup,
                        tabelas.por_periodo(df=fut).reset_index(),
                        tabelas.ticker_mensal(df=fut).reset_index(),
                        tabelas.ticker_anual(df=fut).reset_index(),
                        tabelas.tipo_mensal(df=fut).reset_index(),
                        tabelas.tipo_anual(df=fut).reset_index(),
                    ],
                    nome_planilhas=[
                        "Futuros Extrato Consolidado",
                        "Futuros Por Período",
                        "Futuros Ticker Mensal",
                        "Futuros Tiker Anual",
                        "Futuros Tipo Mensal",
                        "Futuros Tipo Anual",
                    ],
                ),
                file_name="b3_futuros.xlsx",
                key="b3_futuros",
            )

            st.markdown("#### Extrato Futuros")
            st.dataframe(data=fut, use_container_width=True)
            st.markdown("---")

            st.markdown("#### Futuros por Período")
            st.dataframe(
                data=tabelas.por_periodo(df=fut),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Futuros por Ticker - Mensal")
            st.dataframe(
                data=tabelas.ticker_mensal(df=fut),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Futuros por Ticker - Anual")
            st.dataframe(
                data=tabelas.ticker_anual(df=fut),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Futuros por Tipo - Mensal")
            st.dataframe(
                data=tabelas.tipo_mensal(df=fut),
                use_container_width=True,
            )
            st.markdown("---")

            st.markdown("#### Futuros por Tipo - Anual")
            st.dataframe(
                data=tabelas.tipo_anual(df=fut),
                use_container_width=True,
            )
            st.markdown("---")

# MARK: Tela Inicial
else:
    # Mostrar mensagem de erro se o logo não for encontrado
    if not selecionar_imagem:
        st.write("Não foram encontradas imagens na pasta.")

    else:
        logo_path = caminho_pasta_imagens / selecionar_imagem
        img = Image.open(logo_path)
        st.image(img, width=250)

        st.markdown("# B3 Analyzer")

        st.markdown(
            """
            Bem vindo ao B3 Analyzer!

            Este app tem o objetivo de fornecer informações sobre os investimentos na bolsa de valores com base nos extratos fornecidos pela B3.

            Faça o upload dos extratos da B3 na tela lateral para que as análises sejam apresentadas.
            
            **Dica**: faça o download dos extratos por ano na B3, e faça o upload de todos os extratos para ver as informações consolidadas.

            """
        )

        st.markdown("---")

        st.markdown("### Faça o upload dos seus extratos na tela lateral 👈")

        with st.sidebar:

            st.markdown(
                "[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B3V8QAU)"
            )
