import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="🧼 Data Cleaner & Classifier", layout="wide")
st.title("🧼 Mouse Data Cleaner & Classifier")

uploaded_file = st.file_uploader("Upload your dataset (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        filename = uploaded_file.name
        df = None

        if filename.endswith('.csv'):
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            try:
                df = pd.read_csv(stringio, sep=';')
                file_format = 'CSV (semicolon)'
            except:
                stringio.seek(0)
                df = pd.read_csv(stringio, sep=',')
                file_format = 'CSV (comma)'
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
            file_format = 'Excel'
        else:
            st.error("Unsupported file format.")

        if df is not None:
            st.success(f"✅ File loaded! Format: {file_format}")

            if df.shape[1] == 1 and ';' in uploaded_file.getvalue().decode("utf-8"):
                stringio.seek(0)
                df = pd.read_csv(stringio, sep=';', header=None)

            if any(str(col).startswith("Unnamed") for col in df.columns):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

            df.columns = df.columns.astype(str).str.strip()

            # Drop rows with any NaN, '-' or '_'
            def is_invalid(row):
                return any(pd.isna(val) or str(val).strip() in ['-', '_'] for val in row)

            initial_len = len(df)
            df = df[~df.apply(is_invalid, axis=1)].reset_index(drop=True)
            st.write(f"🧹 Dropped {initial_len - len(df)} rows with NaN or junk values (-, _)!")

            # Drop duplicates
            initial_len = len(df)
            df = df[~df.duplicated()].reset_index(drop=True)
            st.write(f"🧹 Dropped {initial_len - len(df)} duplicate rows.")

            # Rename units
            rename_cols = {
                "Length": "Length (mm)",
                "Width": "Width (mm)",
                "Height": "Height (mm)",
                "Weight": "Weight (g)"
            }
            df.rename(columns=rename_cols, inplace=True)

            # Convert to mm
            dim_cols = ["Length (mm)", "Width (mm)", "Height (mm)"]
            for col in dim_cols:
                if col in df.columns:
                    def convert(val):
                        val = str(val).lower().strip()
                        if "cm" in val:
                            return float(val.replace("cm", "")) * 10
                        elif "mm" in val:
                            return float(val.replace("mm", ""))
                        return float(val)
                    df[col] = pd.to_numeric(df[col].apply(convert), errors='coerce')

            df.dropna(subset=dim_cols, inplace=True)

            # Compute Volume & Size Category
            df['Volume (mm^3)'] = df['Length (mm)'] * df['Width (mm)'] * df['Height (mm)']
            bins = [0, 100000, 150000, float('inf')]
            labels = ['Small', 'Medium', 'Large']
            df['Size Category'] = pd.cut(df['Volume (mm^3)'], bins=bins, labels=labels, right=False)
            df['Height'] = df['Volume (mm^3)'].round().astype(int).astype(str) + ' (' + df['Size Category'].astype(str) + ')'

            # Drop volume/dimension cols
            df.drop(columns=dim_cols + ['Volume (mm^3)', 'Size Category'], inplace=True)

            # Reorder 'Height' after 'Weight (g)'
            if 'Height' in df.columns and 'Weight (g)' in df.columns:
                cols = df.columns.tolist()
                h = cols.pop(cols.index('Height'))
                i = cols.index('Weight (g)')
                cols.insert(i + 1, h)
                df = df[cols]

            # Filter UI (visual only)
            with st.expander("🔍 Optional Filter UI", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    if 'Brand' in df.columns:
                        st.multiselect("Brand", df['Brand'].dropna().unique())
                    st.selectbox("Mouse Type", ["", "Gaming", "Normal", "Design/Edit"])
                    st.radio("Subtype", ["Casual", "Hard-core"], horizontal=True)
                    st.selectbox("Sensor Technology", ["Optical", "Laser", "Hybrid"])

                with col2:
                    st.selectbox("Hand Compatibility", ["Right", "Left", "Ambidextrous"])
                    st.slider("Side Buttons", 2, 10, 2)
                    st.slider("Middle Buttons", 0, 3, 0)
                    st.slider("DPI Range", 400, 32000, (800, 1600))
                    st.selectbox("Polling Rate", [125, 500, 1000, 4000, 8000])

            # Final display
            st.subheader("🧾 Final Cleaned Table")
            st.dataframe(df.reset_index(drop=True), use_container_width=True)

    except Exception as e:
        st.error(f"❌ An error occurred during processing: {e}")
