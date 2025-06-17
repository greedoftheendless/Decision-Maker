import streamlit as st
from shared.data_reader import read_dataset

st.set_page_config(page_title="🖱️ Mouse Decision Maker", layout="wide")
st.title("🖱️ Mouse Decision Maker")

uploaded_file = st.file_uploader("Upload your dataset (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df, file_format, encoding, error = read_dataset(uploaded_file)

    if error:
        st.error(f"Error reading file: {error}")
    elif df is not None:
        st.success(f"File loaded! Format: {file_format}, Encoding: {encoding}")

        # Fix single-column CSV split by semicolon
        if df.shape[1] == 1:
            df = df[df.columns[0]].str.split(";", expand=True)

        # Fix unnamed columns with header in first row
        if any(str(col).startswith("Unnamed") for col in df.columns):
            df.columns = df.iloc[0]
            df = df[1:]

        df.columns = df.columns.astype(str).str.strip()

        # Immediately display raw dataframe without filters or buttons
        st.subheader("📊 Uploaded Table")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
else:
    st.info("Please upload a dataset to see the raw data here.")
