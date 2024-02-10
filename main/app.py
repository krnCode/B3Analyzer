import pandas as pd
import streamlit as st

with st.sidebar:
    file = st.file_uploader(label="Envie o extrato em excel (extensão .xlsx)")


if file:
    excel_file = pd.read_excel(
        io=file,
    )
    st.markdown("## Seu extrato:")
    st.dataframe(data=excel_file, use_container_width=True)

else:
    st.markdown("### Faça o upload do seu extrato na tela lateral")
