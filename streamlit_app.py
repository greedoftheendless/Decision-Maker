import streamlit as st
import pandas as pd
import numpy as np
import io
import logging
import sys

from shared.filter_presets import apply_preset_filtration
from shared.custom_filters import apply_custom_filters, apply_categorical_filters, apply_checkbox_filters
from shared.render_filters import render_filters_and_apply

# === LOGGING SETUP ===
logger = logging.getLogger("streamlit_logger")
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s — %(levelname)s — %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="🖱️ Mouse Decision Maker", layout="wide")
st.title("🖱️ Mouse Decision Maker")

# === SESSION STATE INIT ===
for key in ["df", "show_results", "filtered_df", "applied_filters", "current_preset", "last_file"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "df" else False if key == "show_results" else {}

# === FILE UPLOADER ===
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])
if uploaded_file:
    if st.session_state.df is None or uploaded_file.name != st.session_state.last_file:
        try:
            file_format = uploaded_file.name.split('.')[-1].lower()
            df = None

            if file_format == 'csv':
                content = uploaded_file.getvalue().decode("utf-8")
                try:
                    df = pd.read_csv(io.StringIO(content), sep=';')
                except:
                    df = pd.read_csv(io.StringIO(content), sep=',')
            else:
                df = pd.read_excel(uploaded_file)

            if df.shape[1] == 1 and ';' in str(df.columns[0]):
                df = df[df.columns[0]].str.split(';', expand=True)

            if any(str(col).startswith("Unnamed") for col in df.columns):
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

            df.columns = df.columns.astype(str).str.strip()
            df.dropna(how='all', inplace=True)

            def is_junk_row(row):
                return any(str(val).strip() in ['-', '_'] or pd.isna(val) for val in row)

            df = df[~df.apply(is_junk_row, axis=1)].reset_index(drop=True)
            df = df[~df.duplicated(keep='first')]

            numeric_cols = ["Weight (g)", "DPI", "Polling rate", "Side buttons", "Middle buttons", "Height", "Length", "Width"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            st.session_state.df = df
            st.session_state.last_file = uploaded_file.name
            st.success("✅ File processed successfully!")
            logger.info(f"📊 Data loaded. Shape: {df.shape}")

        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.stop()

# === MAIN LOGIC ===
if st.session_state.df is not None:
    df = st.session_state.df
    st.sidebar.header("🎯 Mouse Finder")

    preset_options = ["", "Gaming", "Normal", "Editing", "Ergonomic", "Compact"]
    selected_preset = st.radio("Choose your use case:", preset_options, horizontal=True, index=0)

    if selected_preset:
        descriptions = {
            "": "",
            "Gaming": "🎮 Gaming: Lightweight, responsive, high-DPI",
            "Normal": "💼 Normal: Reliable daily-use mice",
            "Editing": "🎨 Editing: Extra buttons, precision",
            "Ergonomic": "🫲 Ergonomic: Strain-free long use",
            "Compact": "📱 Compact: Lightweight, travel-ready"
        }
        st.markdown(descriptions.get(selected_preset, ""))

        if st.button("🚀 GO - Find My Mice!"):
            filtered_df, applied_filters = apply_preset_filtration(df, selected_preset)
            st.session_state.filtered_df = filtered_df
            st.session_state.applied_filters = applied_filters
            st.session_state.current_preset = selected_preset
            st.session_state.show_results = True
            st.rerun()

    if st.sidebar.button("🔄 Reset", use_container_width=True):
        st.session_state.show_results = False
        st.session_state.filtered_df = None
        st.session_state.applied_filters = {}
        st.session_state.current_preset = ""
        st.rerun()

    if st.session_state.show_results and st.session_state.filtered_df is not None:
        filtered_df = st.session_state.filtered_df
        applied_filters = st.session_state.applied_filters
        current_preset = st.session_state.current_preset

        filtered_df, custom_filters, category_filters, checkbox_filters = render_filters_and_apply(filtered_df)

        st.header(f"🎯 {current_preset} Mice Results")
        st.subheader(f"Found {len(filtered_df)} matching mice")

        if len(filtered_df) == 0:
            st.warning("😕 No results after applying filters.")
        else:
            st.subheader("🔍 Applied Preset Filters")
            cols = st.columns(2)
            for i, (k, v) in enumerate(applied_filters.items()):
                with cols[i % 2]:
                    st.write(f"**{k}:** {v}")
            st.divider()

            # === OVERVIEW METRICS ===
            st.subheader("📊 Overview")
            col1, col2, col3, col4 = st.columns(4)

            display_df = filtered_df.copy()

            if all(col in display_df.columns for col in ["Height (mm)", "Width (mm)", "Length (mm)"]):
                display_df["Volume"] = (
                    display_df["Height (mm)"] *
                    display_df["Width (mm)"] *
                    display_df["Length (mm)"]
                )

                def size_category(vol):
                    if vol < 287907:
                        return "Small"
                    elif vol < 324720:
                        return "Medium"
                    else:
                        return "Large"

                display_df["Size"] = display_df["Volume"].apply(size_category)
                avg_size = size_category(display_df["Volume"].mean())
                col1.metric("Avg Size", avg_size)
            else:
                display_df["Size"] = "Unknown"
                col1.metric("Avg Size", "N/A")

            if "DPI" in display_df.columns:
                col2.metric("Avg DPI", f"{display_df['DPI'].mean():.0f}")
            if "Side buttons" in display_df.columns:
                col3.metric("Avg Buttons", f"{display_df['Side buttons'].mean():.1f}")
            if "Brand" in display_df.columns:
                col4.metric("Brands", display_df["Brand"].nunique())

            if "Weight (g)" in display_df.columns:
                def weight_category(w):
                    if pd.isna(w): return "Unknown"
                    if w < 78: return "Light"
                    elif w <= 99: return "Medium"
                    else: return "Heavy"

                display_df["Weight (Light/Heavy)"] = display_df["Weight (g)"].apply(
                    lambda w: f"{int(w)}g ({weight_category(w)})" if not pd.isna(w) else "N/A"
                )
                display_df.drop(columns=["Weight (g)"], inplace=True)

            display_df.drop(columns=["Volume", "Height", "Width", "Length", "Volume"], errors="ignore", inplace=True)

            st.divider()
            st.subheader("🖱️ Recommended Mice")
            st.dataframe(display_df.reset_index(drop=True), use_container_width=True, height=500)
            st.download_button(
                "📅 Download Results",
                data=display_df.to_csv(index=False),
                file_name=f"{current_preset.lower()}_mice_filtered.csv",
                mime="text/csv"
            )
    else:
        st.header("📊 Mouse Dataset Overview")
        st.subheader(f"Total mice: {len(df)}")
        st.info("👈 Choose a preset to filter your list.")
        st.dataframe(df, use_container_width=True)

else:
    st.header("Welcome to Mouse Decision Maker! 🖱️")
    st.subheader("Find your perfect mouse with smart filters.")
    st.markdown("""
        1. **Upload** a CSV or Excel with mouse specs  
        2. **Pick a preset** for Gaming, Editing, Travel...  
        3. **Fine-tune** using DPI, shape, connection, etc.  
        4. **Export** the final list as a CSV
    """)
