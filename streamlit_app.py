import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="🖱️ Mouse Decision Maker", layout="wide")
st.title("🖱️ Mouse Decision Maker")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        file_format = uploaded_file.name.split('.')[-1].lower()
        df = None

        # Try reading
        if file_format == 'csv':
            content = uploaded_file.getvalue().decode("utf-8")
            try:
                df = pd.read_csv(io.StringIO(content), sep=';')
            except:
                df = pd.read_csv(io.StringIO(content), sep=',')

        elif file_format in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format.")

        # Fix single-column issue
        if df.shape[1] == 1 and ';' in df.columns[0]:
            df = df[df.columns[0]].str.split(';', expand=True)

        # Fix headers if unnamed
        if any(str(col).startswith("Unnamed") for col in df.columns):
            df.columns = df.iloc[0]
            df = df[1:]

        df.columns = df.columns.astype(str).str.strip()

        # Drop empty or junk rows
        df.dropna(how='all', inplace=True)

        def is_junk_row(row):
            return any(str(val).strip() in ['-', '_'] or pd.isna(val) for val in row)

        df = df[~df.apply(is_junk_row, axis=1)].reset_index(drop=True)
        df = df[~df.duplicated(keep='first')]

        # Drop rows missing dimensions
        dimension_cols = ["Length", "Width", "Height"]
        df.dropna(subset=[col for col in dimension_cols if col in df.columns], inplace=True)

        # Rename and convert
        rename_map = {
            "Length": "Length (mm)",
            "Width": "Width (mm)",
            "Height": "Height (mm)"
        }
        df.rename(columns=rename_map, inplace=True)

        for col in ["Length (mm)", "Width (mm)", "Height (mm)"]:
            if col in df.columns:
                def convert(val):
                    try:
                        val = str(val).lower().strip()
                        if 'cm' in val:
                            return float(val.replace("cm", "")) * 10
                        elif 'mm' in val:
                            return float(val.replace("mm", ""))
                        return float(val)
                    except:
                        return np.nan
                df[col] = df[col].apply(convert)

        df.dropna(subset=["Length (mm)", "Width (mm)", "Height (mm)"], inplace=True)

        # Volume & Size
        df['Volume (mm^3)'] = df["Length (mm)"] * df["Width (mm)"] * df["Height (mm)"]
        bins = [0, 100000, 150000, float("inf")]
        labels = ["Small", "Medium", "Large"]
        df["Size"] = df["Volume (mm^3)"].round().astype(int).astype(str) + " (" + pd.cut(df["Volume (mm^3)"], bins=bins, labels=labels).astype(str) + ")"

        df.drop(columns=["Length (mm)", "Width (mm)", "Height (mm)", "Volume (mm^3)"], inplace=True)
        df.dropna(inplace=True)

        st.success("✅ File processed successfully!")

        # === FILTER UI ===
        st.sidebar.header("🧩 Visual Filters (UI only)")
        filter_columns = [
            "Brand", "Name", "Weight (g)", "Shape", "Hump placement", "Front flare",
            "Side curvature", "Hand compatibility", "Thumb rest", "Ring finger rest",
            "Material", "Connectivity", "Sensor", "Sensor technology", "Sensor position",
            "DPI", "Polling rate", "Tracking speed (IPS)", "Acceleration (G)",
            "Side buttons", "Middle buttons"
        ]

        for col in filter_columns:
            if col in df.columns:
                values = df[col].dropna().unique().tolist()
                if df[col].dtype == object or isinstance(values[0], str):
                    st.sidebar.multiselect(col, options=sorted(values))
                else:
                    st.sidebar.slider(col, float(df[col].min()), float(df[col].max()))

        # === Final Table ===
        st.subheader("📊 Cleaned Table with Size Classification")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
