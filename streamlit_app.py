import streamlit as st
import pandas as pd
import numpy as np
import io

st.title("Data Cleaning App")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        filename = uploaded_file.name
        file_format = ''
        df = None  # Initialize df to None

        if filename.endswith('.csv'):
            # Read as string to handle potential encoding issues and then parse
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            # Attempt to read with semicolon delimiter first
            try:
                df = pd.read_csv(stringio, sep=';')
                file_format = 'CSV'
                st.success(f"File loaded with semicolon delimiter! Format: {file_format}")
            except Exception as e_semicolon:
                st.warning(f"Could not read with semicolon delimiter: {e_semicolon}. Trying comma delimiter...")
                stringio.seek(0)  # Reset stream position
                try:
                    df = pd.read_csv(stringio, sep=',')
                    file_format = 'CSV'
                    st.success(f"File loaded with comma delimiter! Format: {file_format}")
                except Exception as e_comma:
                    st.error(f"Could not read with comma delimiter either: {e_comma}")
                    df = None  # Ensure df is None if reading fails

        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=0)
            file_format = 'Excel'
            st.success(f"File loaded! Format: {file_format}")
        else:
            st.error("Unsupported file format.")
            df = None

        if df is not None:
            # Handle semi-colon separated single column if still one column after initial read (only for CSV)
            if file_format == 'CSV' and df.shape[1] == 1 and ';' in uploaded_file.getvalue().decode("utf-8"):
                st.warning("CSV read as a single column, attempting to split with semicolon...")
                stringio.seek(0)  # Reset stream position
                # Read again, this time splitting the single column
                df = pd.read_csv(stringio, sep=';', header=None)  # Read without header initially for splitting

            # Fix headers if unnamed - this step is crucial after potential splitting
            if any(str(col).startswith("Unnamed") for col in df.columns):
                st.warning("Unnamed columns detected, attempting to fix headers...")
                new_headers = df.iloc[0]
                df = df[1:].reset_index(drop=True)
                df.columns = new_headers

            df.columns = df.columns.astype(str).str.strip()

            # Treat '-', '_', and blank strings as missing
            df.replace(['-', '_', ' '], np.nan, inplace=True)

            # Drop rows with any missing data
            initial_rows = len(df)
            df.dropna(how='any', inplace=True)
            rows_dropped_empty = initial_rows - len(df)
            if rows_dropped_empty > 0:
                st.write(f"Dropped {rows_dropped_empty} rows with missing or junk values.")

            # Drop duplicate rows
            initial_rows = len(df)
            df = df[~df.duplicated(keep='first')].reset_index(drop=True)
            rows_dropped_duplicates = initial_rows - len(df)
            if rows_dropped_duplicates > 0:
                st.write(f"Dropped {rows_dropped_duplicates} duplicate rows.")

            # Rename dimension columns
            unit_cols = {
                "Length": "Length (mm)",
                "Width": "Width (mm)",
                "Height": "Height (mm)",
                "Weight": "Weight (g)"
            }
            for old, new in unit_cols.items():
                if old in df.columns:
                    df.rename(columns={old: new}, inplace=True)

            # Improved conversion function
            def convert_cm_to_mm(value):
                try:
                    value = str(value).lower().strip()
                    if "cm" in value:
                        return float(value.replace("cm", "").strip()) * 10
                    elif "mm" in value:
                        return float(value.replace("mm", "").strip())
                    else:
                        # Assume mm if unit is not given
                        return float(value)
                except:
                    return np.nan

            # Apply conversion to applicable columns
            for col in ["Length (mm)", "Width (mm)", "Height (mm)"]:
                if col in df.columns:
                    df[col] = df[col].apply(convert_cm_to_mm)

            st.subheader("Cleaned & Final Table:")
            st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred during file processing: {e}")
